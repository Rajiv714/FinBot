import os
from datetime import datetime
from typing import Dict, Any
from agents.content_extractor import ContentExtractorAgent
from agents.topic_analyzer import TopicAnalyzerAgent
from agents.handout_generator import HandoutGeneratorAgent
from agents.quality_assessor import QualityAssessorAgent
from agents.google_search_agent import GoogleSearchAgent
from llm.gemini import create_gemini_service
from embeddings.embeddings import create_embedding_service
from vectorstore.qdrant_client import create_qdrant_client

class FinBotHandoutCreator:
    """Enhanced handout creator using FinBot's multi-agent system"""
    
    def __init__(self):
        print("Initializing FinBot Handout Creator...")
        
        # Initialize FinBot services using factory functions
        self.gemini_service = create_gemini_service()
        
        embedding_service = create_embedding_service()
        embedding_dim = embedding_service.get_embedding_dimension()
        
        self.vector_store = create_qdrant_client(vector_size=embedding_dim)
        
        # Initialize agents using FinBot services
        self.content_extractor = ContentExtractorAgent(self.gemini_service, self.vector_store)
        self.google_search = GoogleSearchAgent(self.gemini_service, self.vector_store)
        self.topic_analyzer = TopicAnalyzerAgent(self.gemini_service, self.vector_store)
        self.handout_generator = HandoutGeneratorAgent(self.gemini_service, self.vector_store)
        self.quality_assessor = QualityAssessorAgent(self.gemini_service, self.vector_store)
        
        # Ensure handout directory exists
        self.handout_dir = "Handout"
        os.makedirs(self.handout_dir, exist_ok=True)
        
        print("All agents initialized successfully!")

    def create_handout(self, topic: str) -> Dict[str, Any]:
        """Create comprehensive handout using multi-agent collaboration"""
        
        print(f"Starting handout creation for: '{topic}'")
        
        output_data = {
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'agent_outputs': {},
            'final_metrics': {}
        }
        
        # Phase 1: Extract content from vector database
        print("Phase 1: Extracting content from financial documents...")
        vector_extraction = self.content_extractor.execute({'topic': topic})
        output_data['agent_outputs']['vector_extraction'] = vector_extraction
        print(f"   Extracted {vector_extraction['word_count']} words from {vector_extraction['source_count']} sources")
        
        # Phase 2: Google Search for additional content
        print("Phase 2: Searching Google for additional financial information...")
        try:
            google_extraction = self.google_search.execute({
                'topic': topic,
                'search_depth': 'standard'
            })
            output_data['agent_outputs']['google_extraction'] = google_extraction
            print(f"   Found {len(google_extraction.get('processed_results', []))} relevant search results")
        except Exception as e:
            print(f"   Google search failed: {e}")
            google_extraction = {'processed_results': [], 'structured_content': {}}
            output_data['agent_outputs']['google_extraction'] = google_extraction
        
        # Phase 3: Analyze topic and content
        print("Phase 3: Analyzing topic and content structure...")
        analysis_result = self.topic_analyzer.execute({
            'topic': topic,
            'vector_content': vector_extraction['extracted_content'],
            'google_content': google_extraction.get('structured_content', {})
        })
        output_data['agent_outputs']['topic_analysis'] = analysis_result
        print(f"   Analysis completed")
        
        # Phase 4: Generate handout
        print("Phase 4: Generating comprehensive handout...")
        handout_result = self.handout_generator.execute({
            'topic': topic,
            'vector_content': vector_extraction['extracted_content'],
            'google_content': google_extraction.get('structured_content', {}),
            'analysis': analysis_result,
            'target_length': 3000
        })
        output_data['agent_outputs']['handout_generation'] = handout_result
        print(f"   Generated {handout_result['word_count']} word handout")
        
        # Phase 5: Quality assessment
        print("Phase 5: Assessing and improving quality...")
        current_handout = handout_result['handout_content']
        
        assessment = self.quality_assessor.execute({
            'handout_content': current_handout,
            'topic': topic
        })
        
        output_data['agent_outputs']['quality_assessment'] = assessment
        print(f"   Quality score: {assessment.get('quality_score', 'N/A')}")
        
        # Save handout to file
        filename = f"{topic.replace(' ', '_').replace('/', '_')}_handout.md"
        filepath = os.path.join(self.handout_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {topic} - Financial Education Handout\n\n")
            f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write(current_handout)
        
        output_data['handout_filepath'] = filepath
        output_data['handout_content'] = current_handout
        
        # Calculate final metrics
        output_data['final_metrics'] = {
            'final_handout_words': handout_result['word_count'],
            'quality_score': assessment.get('quality_score', 0),
            'vector_sources': vector_extraction['source_count'],
            'google_results': len(google_extraction.get('processed_results', [])),
            'agent_phases': 5
        }
        
        self._print_summary(output_data)
        
        return output_data
    
    def _print_summary(self, handout_data: Dict):
        """Print creation summary"""
        metrics = handout_data['final_metrics']
        
        print(f"\n{'='*50}")
        print(f"HANDOUT CREATION SUMMARY")
        print(f"{'='*50}")
        print(f"Topic: {handout_data['topic']}")
        print(f"Final handout: {metrics['final_handout_words']:,} words")
        print(f"Quality score: {metrics['quality_score']}")
        print(f"Vector DB sources: {metrics['vector_sources']}")
        print(f"Google search results: {metrics['google_results']}")
        print(f"Saved to: {handout_data['handout_filepath']}")

def run_handout_creator():
    """Interactive handout creator interface"""
    print("FinBot Advanced Handout Creator")
    print("Generate comprehensive financial education handouts")
    
    creator = FinBotHandoutCreator()
    
    while True:
        print("\nSuggested financial topics:")
        print("- Mutual Funds")
        print("- Personal Finance Basics")
        print("- Investment Strategies")
        print("- Retirement Planning")
        print("- Tax Planning")
        print("- Insurance Planning")
        print("- Credit Management")
        
        topic = input("\nEnter handout topic (or 'quit' to exit): ").strip()
        
        if topic.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        if not topic:
            print("Please enter a valid topic")
            continue
            
        try:
            result = creator.create_handout(topic)
            
            print(f"\nHandout creation completed successfully!")
            print(f"Check the file: {result['handout_filepath']}")
                
        except Exception as e:
            print(f"\nError during handout creation: {e}")

if __name__ == "__main__":
    run_handout_creator()