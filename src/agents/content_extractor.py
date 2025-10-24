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
        
        # Enhanced content extraction prompt
        extraction_prompt = f"""
        You are a technical content extraction specialist. Extract comprehensive information about '{topic}' from the provided documents.
        
        Categorize the extracted content into these detailed sections:
        
        ## 1. CORE CONCEPTS & DEFINITIONS (Target: 400+ words)
        - Fundamental definitions and terminology
        - Basic principles and underlying theory
        - Historical development and evolution
        - Key characteristics and properties
        
        ## 2. TECHNICAL SPECIFICATIONS & PARAMETERS (Target: 500+ words)
        - Detailed technical parameters and measurements
        - Performance characteristics and specifications
        - Industry standards and regulatory requirements
        - Equipment specifications and capabilities
        
        ## 3. OPERATIONAL PROCEDURES & BEST PRACTICES (Target: 600+ words)
        - Step-by-step operational processes
        - Setup and configuration procedures
        - Maintenance and calibration requirements
        - Industry best practices and guidelines
        
        ## 4. SAFETY GUIDELINES & PRECAUTIONS (Target: 400+ words)
        - Safety protocols and procedures
        - Risk assessment and management
        - Emergency response procedures
        - Compliance and regulatory requirements
        
        ## 5. COMMON ISSUES & TROUBLESHOOTING (Target: 500+ words)
        - Frequent problems and their symptoms
        - Diagnostic procedures and methods
        - Solution methodologies and fixes
        - Preventive measures and maintenance
        
        ## 6. REAL-WORLD EXAMPLES & CASE STUDIES (Target: 400+ words)
        - Industry applications and use cases
        - Success stories and implementations
        - Lessons learned and best practices
        - Comparative analysis and benchmarks
        
        Documents context: {extraction_results['combined_context'][:4000]}
        
        Generate comprehensive, technical content with specific details, numbers, procedures, and examples.
        Minimum target: 2800 words total across all sections.
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
        """Extract content using multiple search strategies"""
        
        # Strategy 1: Direct topic search
        topic_embedding = self.model.encode([topic])[0]
        direct_chunks = self.vector_store.search(
            query_embedding=topic_embedding, limit=10
        )
        
        # Strategy 2: Technical aspects search
        technical_query = f"{topic} technical specifications parameters standards"
        technical_embedding = self.model.encode([technical_query])[0]
        technical_chunks = self.vector_store.search(
            query_embedding=technical_embedding, limit=8
        )
        
        # Strategy 3: Application and case studies search
        application_query = f"{topic} applications case studies real world examples industry"
        application_embedding = self.model.encode([application_query])[0]
        application_chunks = self.vector_store.search(
            query_embedding=application_embedding, limit=8
        )
        
        # Strategy 4: Safety and troubleshooting search
        safety_query = f"{topic} safety procedures troubleshooting maintenance issues"
        safety_embedding = self.model.encode([safety_query])[0]
        safety_chunks = self.vector_store.search(
            query_embedding=safety_embedding, limit=8
        )
        
        # Strategy 5: Best practices and standards search
        standards_query = f"{topic} best practices industry standards guidelines protocols"
        standards_embedding = self.model.encode([standards_query])[0]
        standards_chunks = self.vector_store.search(
            query_embedding=standards_embedding, limit=8
        )
        
        # Combine all contexts
        all_chunks = direct_chunks + technical_chunks + application_chunks + safety_chunks + standards_chunks
        combined_context = "\n".join([doc.get("text", "") for doc in all_chunks])
        
        return {
            'combined_context': combined_context,
            'total_sources': len(all_chunks),
            'strategies_used': ['direct_search', 'technical_search', 'application_search', 'safety_search', 'standards_search'],
            'chunk_counts': {
                'direct': len(direct_chunks),
                'technical': len(technical_chunks),
                'application': len(application_chunks),
                'safety': len(safety_chunks),
                'standards': len(standards_chunks)
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
