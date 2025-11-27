from .base_agent import BaseAgent
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer

class ContentExtractorAgent(BaseAgent):
    def __init__(self, api_client, vector_store, model_name: str = "BAAI/bge-large-en-v1.5"):
        super().__init__(api_client, vector_store, "ContentExtractor")
        self.model = SentenceTransformer(model_name)
        
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and categorize content from documents"""
        topic = input_data.get('topic')
        
        # Enhanced content extraction with multiple search strategies
        extraction_results = self._extract_comprehensive_content(topic)
        
        # Simplified content extraction prompt for 1000-1200 word handouts
        extraction_prompt = f"""
        You are a content extraction specialist. Extract relevant information about '{topic}' from the provided documents.
        
        Organize the extracted content into these sections:
        
        ## 1. CORE CONCEPTS & DEFINITIONS (150-200 words)
        - Key definitions and terminology
        - Basic principles and fundamentals
        - What it is and why it matters
        
        ## 2. PRACTICAL INFORMATION (200-250 words)
        - How it works in practice
        - Real-world applications and examples
        - Key features or characteristics
        - Common types or categories
        
        ## 3. IMPORTANT CONSIDERATIONS (150-200 words)
        - Benefits and advantages
        - Risks and limitations
        - Best practices
        - Common mistakes to avoid
        
        ## 4. ACTIONABLE INSIGHTS (100-150 words)
        - Getting started steps
        - Tips for success
        - Resources and next steps
        
        Documents context: {extraction_results['combined_context'][:4000]}
        
        Extract clear, relevant information focusing on practical value for learners.
        Target: 600-800 words total extraction.
        """
        
        extracted_content = self.api_client.generate_response(extraction_prompt)
        
        return self.log_execution(
            f"Content extraction for topic: {topic}",
            {
                'topic': topic,
                'extracted_content': extracted_content,
                'content_categories': self._parse_categories(extracted_content),
                'source_count': extraction_results['total_sources'],
                'word_count': len(extracted_content.split()),
                'search_strategies_used': extraction_results['strategies_used']
            }
        )
    
    def _extract_comprehensive_content(self, topic: str) -> Dict[str, Any]:
        """Extract content using 2 focused search strategies (optimized for 1000-1200 words)"""
        
        # Strategy 1: Direct topic search (main content)
        topic_embedding = self.model.encode([topic])[0]
        direct_chunks = self.vector_store.search(
            query_embedding=topic_embedding, limit=15
        )
        
        # Strategy 2: Practical applications and examples
        practical_query = f"{topic} examples applications how to use practical guide"
        practical_embedding = self.model.encode([practical_query])[0]
        practical_chunks = self.vector_store.search(
            query_embedding=practical_embedding, limit=10
        )
        
        # Combine contexts (remove duplicates by checking similarity)
        seen_texts = set()
        all_chunks = []
        
        for chunk in direct_chunks + practical_chunks:
            # Use first 100 chars as rough duplicate check
            chunk_signature = chunk.get("text", "")[:100]
            if chunk_signature not in seen_texts:
                seen_texts.add(chunk_signature)
                all_chunks.append(chunk)
        
        combined_context = "\n\n".join([doc.get("text", "") for doc in all_chunks])
        
        return {
            'combined_context': combined_context,
            'total_sources': len(all_chunks),
            'strategies_used': ['direct_search', 'practical_search'],
            'chunk_counts': {
                'direct': len(direct_chunks),
                'practical': len(practical_chunks),
                'unique': len(all_chunks)
            }
        }
    
    def _parse_categories(self, content: str) -> Dict[str, str]:
        """Parse content into structured categories"""
        categories = {}
        lines = content.split('\n')
        current_category = None
        current_content = []
        
        for line in lines:
            if line.startswith('##') and any(keyword in line.upper() for keyword in 
                ['CORE CONCEPTS', 'TECHNICAL SPECIFICATIONS', 'OPERATIONAL PROCEDURES', 
                 'SAFETY GUIDELINES', 'COMMON ISSUES', 'REAL-WORLD EXAMPLES']):
                if current_category:
                    categories[current_category] = '\n'.join(current_content)
                current_category = line.strip('#').strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_category:
            categories[current_category] = '\n'.join(current_content)
        
        return categories
