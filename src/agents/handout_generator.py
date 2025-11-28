from .base_agent import BaseAgent
from typing import Dict, Any, List

class HandoutGeneratorAgent(BaseAgent):
    def __init__(self, api_client, vector_store):
        super().__init__(api_client, vector_store, "HandoutGenerator")
        
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive handout content"""
        topic = input_data.get('topic')
        
        # Handle different parameter names from Handout_Creator
        vector_content = input_data.get('vector_content', '')
        google_content = input_data.get('google_content', {})
        analysis = input_data.get('analysis', {})
        target_length = input_data.get('target_length', 8000)
        
        # Extract data from analysis result
        analysis_result = analysis.get('analysis_result', '') if isinstance(analysis, dict) else str(analysis)
        enhancement_suggestions = analysis.get('enhancement_suggestions', []) if isinstance(analysis, dict) else []
        content_gaps = analysis.get('identified_gaps', []) if isinstance(analysis, dict) else []
        recommended_sections = analysis.get('recommended_sections', []) if isinstance(analysis, dict) else []
        
        # Ensure content is string for word counting
        extracted_content = vector_content if isinstance(vector_content, str) else str(vector_content)
        analysis_text = analysis_result if isinstance(analysis_result, str) else str(analysis_result)
        
        # Calculate input content metrics safely
        extracted_word_count = len(extracted_content.split()) if extracted_content else 0
        analysis_word_count = len(analysis_text.split()) if analysis_text else 0
        input_word_count = extracted_word_count + analysis_word_count
        
        # Handle google_content which might be structured differently
        google_text = ""
        if isinstance(google_content, dict):
            # Extract relevant text from google content structure
            categorized = google_content.get('categorized_content', {})
            for category, items in categorized.items():
                if items and isinstance(items, list):
                    for item in items[:2]:  # Top 2 from each category
                        if isinstance(item, dict):
                            google_text += item.get('content', '') + "\n"
        
        generation_prompt = f"""
        You are a financial education specialist creating a concise, educational handout for '{topic}'.
        
        TARGET: {target_length} words (1000-1200 words range)
        
        AVAILABLE CONTENT:
        
        1. KNOWLEDGE BASE CONTENT ({extracted_word_count} words):
        {extracted_content[:3000]}
        
        2. LATEST INFORMATION & NEWS:
        {google_text[:1500] if google_text else "No external search results available"}
        
        CREATE A WELL-STRUCTURED EDUCATIONAL HANDOUT with the following structure:
        
        # {topic.title() if topic else 'Topic'} - Financial Education Handout
        
        ## 1. Introduction & Overview (180-200 words)
        - Clear definition and explanation of {topic}
        - Why this topic is important for financial literacy
        - What readers will learn from this handout
        - Brief context about current relevance (include latest news if available)
        
        ## 2. Key Concepts & Fundamentals (250-280 words)
        - Essential terminology and definitions
        - Core principles and how it works
        - Important characteristics or features
        - Common types or categories (if applicable)
        - Basic mechanics explained simply
        
        ## 3. Practical Applications & Examples (250-280 words)
        - Real-world use cases and scenarios
        - Specific examples that illustrate the concepts
        - Who benefits and how
        - Typical situations where this applies
        - Step-by-step example if applicable
        
        ## 4. Important Considerations & Best Practices (200-220 words)
        - Key factors to consider
        - Potential risks and limitations
        - Common mistakes to avoid
        - Best practices and guidelines
        - Tips for success
        - When to seek professional advice
        
        ## 5. Getting Started & Resources (150-170 words)
        - Actionable next steps for readers
        - How to begin or implement
        - Recommended resources for learning more
        - Professional organizations or certifications
        - Where to get help or guidance
        
        WRITING GUIDELINES:
        - Use clear, accessible language for general audience
        - Balance educational value with readability
        - Include specific numbers, dates, or data points when available
        - Use real examples to illustrate concepts
        - Incorporate latest news or trends from google search results
        - Maintain professional but friendly tone
        - Use bullet points and lists for clarity
        - Avoid excessive jargon; explain technical terms
        - Focus on practical, actionable information
        - Keep paragraphs concise (3-5 sentences)
        
        WORD COUNT TARGETS:
        - Section 1: ~190 words
        - Section 2: ~265 words  
        - Section 3: ~265 words
        - Section 4: ~210 words
        - Section 5: ~160 words
        - Total: ~1090-1190 words
        
        Generate a well-structured, informative, and engaging handout that provides real value to readers learning about {topic}.
        """
        
        handout_content = self.api_client.generate_response(generation_prompt)
        
        # Calculate output metrics
        output_word_count = len(handout_content.split())
        section_count = handout_content.count('##')
        content_expansion_ratio = output_word_count / input_word_count if input_word_count > 0 else 0
        
        return self.log_execution(
            f"Handout generation for: {topic}",
            {
                'topic': topic,
                'handout_content': handout_content,
                'word_count': output_word_count,
                'section_count': section_count,
                'content_sources': {
                    'extraction_words': len(extracted_content.split()),
                    'analysis_words': len(analysis_result.split()),
                    'total_input_words': input_word_count,
                    'enhancements_used': len(enhancement_suggestions),
                    'gaps_addressed': len(content_gaps)
                },
                'content_expansion_ratio': content_expansion_ratio,
                'quality_metrics': self._calculate_quality_metrics(handout_content)
            }
        )
    
    def _calculate_quality_metrics(self, content: str) -> Dict[str, Any]:
        """Calculate quality metrics for the generated handout"""
        
        lines = content.split('\n')
        sections = [line for line in lines if line.startswith('##')]
        
        # Count different types of content
        bullet_points = sum(1 for line in lines if line.strip().startswith('-'))
        numbered_lists = sum(1 for line in lines if line.strip() and line.strip()[0].isdigit() and '.' in line[:5])
        
        # Estimate technical content density
        technical_keywords = ['specifications', 'parameters', 'procedure', 'protocol', 'standard', 'regulation', 'compliance', 'safety', 'maintenance', 'troubleshooting']
        technical_density = sum(content.lower().count(keyword) for keyword in technical_keywords)
        
        return {
            'total_sections': len(sections),
            'bullet_points': bullet_points,
            'numbered_procedures': numbered_lists,
            'technical_keyword_density': technical_density,
            'average_section_length': len(content.split()) / len(sections) if sections else 0,
            'readability_score': self._estimate_readability(content)
        }
    
    def _estimate_readability(self, content: str) -> str:
        """Estimate readability level of the content"""
        words = content.split()
        sentences = content.count('.') + content.count('!') + content.count('?')
        
        if sentences == 0:
            return "Unknown"
        
        avg_words_per_sentence = len(words) / sentences
        
        if avg_words_per_sentence < 15:
            return "High (Easy to read)"
        elif avg_words_per_sentence < 25:
            return "Medium (Moderate complexity)"
        else:
            return "Low (Technical/Complex)"
