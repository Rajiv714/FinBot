"""
Handout generation service - Business logic for educational content creation
Uses 3 agents: ContentExtractor + GoogleSearch + HandoutGenerator
Target: 1000-1200 words
"""
import sys
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add src directory to path
src_path = str(Path(__file__).parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from agents.content_extractor import ContentExtractorAgent
from agents.google_search_agent import GoogleSearchAgent
from agents.handout_generator import HandoutGeneratorAgent
from llm.gemini import create_gemini_service
from embeddings.embeddings import create_embedding_service
from vectorstore.qdrant_client import create_qdrant_client


class HandoutService:
    """Service for generating educational handouts"""
    
    def __init__(self):
        """Initialize handout service with agents"""
        print("Initializing Handout Service...")
        
        # Initialize core services
        # Use "handout" use_case for longer output (2048 tokens)
        self.gemini_service = create_gemini_service(use_case="handout")
        embedding_service = create_embedding_service()
        embedding_dim = embedding_service.get_embedding_dimension()
        self.vector_store = create_qdrant_client(vector_size=embedding_dim)
        
        # Initialize 3 agents
        self.content_extractor = ContentExtractorAgent(
            self.gemini_service, 
            self.vector_store
        )
        self.google_search = GoogleSearchAgent(
            self.gemini_service, 
            self.vector_store
        )
        self.handout_generator = HandoutGeneratorAgent(
            self.gemini_service, 
            self.vector_store
        )
        
        # Ensure handout directory exists
        self.handout_dir = Path(__file__).parent.parent.parent / "Handout"
        self.handout_dir.mkdir(exist_ok=True)
        
        print("Handout Service initialized successfully!")
    
    def create_handout(
        self,
        topic: str,
        target_length: int = 1200,
        include_google_search: bool = True,
        search_depth: str = "standard"
    ) -> Dict[str, Any]:
        """
        Create educational handout using 3-agent pipeline.
        
        Args:
            topic: Topic for the handout
            target_length: Target word count (1000-1200)
            include_google_search: Whether to use Google search
            search_depth: Search depth (basic, standard, comprehensive)
            
        Returns:
            Dictionary with handout content and metadata
        """
        start_time = time.time()
        agent_outputs = []
        
        try:
            print(f"Starting handout creation for: '{topic}'")
            
            # ================================================================
            # PHASE 1: Extract content from vector database
            # ================================================================
            print("Phase 1: Extracting content from knowledge base...")
            phase1_start = time.time()
            
            vector_extraction = self.content_extractor.execute({'topic': topic})
            phase1_time = time.time() - phase1_start
            
            agent_outputs.append({
                "agent_name": "ContentExtractor",
                "execution_time": phase1_time,
                "word_count": vector_extraction.get('word_count', 0),
                "success": True,
                "data": {
                    "source_count": vector_extraction.get('source_count', 0),
                    "strategies_used": vector_extraction.get('search_strategies_used', [])
                }
            })
            
            print(f"   ✓ Extracted {vector_extraction['word_count']} words from {vector_extraction['source_count']} sources")
            print(f"   Time: {phase1_time:.2f}s")
            
            # ================================================================
            # PHASE 2: Google Search for latest information (optional)
            # ================================================================
            google_extraction = {'processed_results': [], 'structured_content': {}}
            
            if include_google_search:
                print(f"Phase 2: Searching for latest news and information...")
                phase2_start = time.time()
                
                try:
                    google_extraction = self.google_search.execute({
                        'topic': topic,
                        'search_depth': search_depth
                    })
                    phase2_time = time.time() - phase2_start
                    
                    agent_outputs.append({
                        "agent_name": "GoogleSearch",
                        "execution_time": phase2_time,
                        "word_count": len(str(google_extraction.get('structured_content', {}))).split().__len__(),
                        "success": True,
                        "data": {
                            "results_count": len(google_extraction.get('processed_results', [])),
                            "search_queries": google_extraction.get('search_queries', [])
                        }
                    })
                    
                    print(f"   ✓ Found {len(google_extraction.get('processed_results', []))} relevant results")
                    print(f"   Time: {phase2_time:.2f}s")
                    
                except Exception as e:
                    print(f"   ⚠ Google search failed: {e}")
                    agent_outputs.append({
                        "agent_name": "GoogleSearch",
                        "execution_time": time.time() - phase2_start,
                        "word_count": 0,
                        "success": False,
                        "data": {"error": str(e)}
                    })
            else:
                print("Phase 2: Google search skipped")
            
            # ================================================================
            # PHASE 3: Generate handout (1000-1200 words)
            # ================================================================
            print(f"Phase 3: Generating {target_length}-word handout...")
            phase3_start = time.time()
            
            handout_result = self.handout_generator.execute({
                'topic': topic,
                'vector_content': vector_extraction.get('extracted_content', ''),
                'google_content': google_extraction.get('structured_content', {}),
                'target_length': target_length
            })
            phase3_time = time.time() - phase3_start
            
            agent_outputs.append({
                "agent_name": "HandoutGenerator",
                "execution_time": phase3_time,
                "word_count": handout_result.get('word_count', 0),
                "success": True,
                "data": {
                    "section_count": handout_result.get('section_count', 0),
                    "quality_metrics": handout_result.get('quality_metrics', {})
                }
            })
            
            print(f"   ✓ Generated {handout_result['word_count']} word handout")
            print(f"   Time: {phase3_time:.2f}s")
            
            # ================================================================
            # Save handout to file
            # ================================================================
            handout_content = handout_result.get('handout_content', '')
            filename = f"{topic.replace(' ', '_').replace('/', '_')}_handout.md"
            filepath = self.handout_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {topic} - Financial Education Handout\n\n")
                f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                f.write(handout_content)
            
            total_time = time.time() - start_time
            
            print(f"\n{'='*60}")
            print(f"✓ HANDOUT CREATION COMPLETED")
            print(f"{'='*60}")
            print(f"Topic: {topic}")
            print(f"Word count: {handout_result['word_count']:,} words")
            print(f"Total time: {total_time:.2f}s")
            print(f"Saved to: {filepath}")
            print(f"{'='*60}")
            
            return {
                "success": True,
                "topic": topic,
                "handout_content": handout_content,
                "word_count": handout_result['word_count'],
                "filepath": str(filepath),
                "agent_outputs": agent_outputs,
                "total_execution_time": total_time
            }
            
        except Exception as e:
            total_time = time.time() - start_time
            print(f"\n✗ ERROR during handout creation: {str(e)}")
            
            return {
                "success": False,
                "topic": topic,
                "handout_content": "",
                "word_count": 0,
                "filepath": None,
                "agent_outputs": agent_outputs,
                "total_execution_time": total_time,
                "error": str(e)
            }


# Global service instance
_handout_service = None


def get_handout_service() -> HandoutService:
    """Get or create handout service singleton"""
    global _handout_service
    if _handout_service is None:
        _handout_service = HandoutService()
    return _handout_service
