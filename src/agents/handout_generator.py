from .base_agent import BaseAgent
from typing import Dict, Any, List

class HandoutGeneratorAgent(BaseAgent):
    def __init__(self, api_client, vector_store):
        super().__init__(api_client, vector_store, "HandoutGenerator")
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
        
        generation_prompt = f"""
        You are a technical documentation specialist creating a comprehensive handout for '{topic}'.
        
        You have access to:
        - {extracted_word_count} words of extracted technical content
        - {analysis_word_count} words of detailed analysis
        - {len(enhancement_suggestions)} specific enhancement opportunities
        - {len(content_gaps)} identified content gaps to address
        - {len(recommended_sections)} additional sections to include
        
        CONTENT INPUTS:
        
        1. EXTRACTED TECHNICAL CONTENT:
        {extracted_content[:4000]}...
        
        2. ANALYSIS INSIGHTS:
        {analysis_text[:2000]}...
        
        3. ENHANCEMENT OPPORTUNITIES:
        {chr(10).join([f"- {enh.get('enhancement_description', str(enh)) if isinstance(enh, dict) else str(enh)}" for enh in enhancement_suggestions[:10]])}
        
        4. CONTENT GAPS TO ADDRESS:
        {chr(10).join([f"- {gap.get('gap_description', str(gap)) if isinstance(gap, dict) else str(gap)}" for gap in content_gaps[:10]])}
        
        5. RECOMMENDED ADDITIONAL SECTIONS:
        {chr(10).join([f"- {section}" for section in recommended_sections[:5]])}
        
        CREATE A COMPREHENSIVE HANDOUT with the following structure and requirements:
        
        # {topic.title() if topic else 'Topic'} - Comprehensive Technical Handout
        
        ## 1. Executive Summary & Learning Objectives (600+ words)
        - Purpose, scope, and importance of the topic
        - Clear learning objectives and outcomes
        - Overview of key concepts covered
        - Target audience and prerequisites
        - Key benefits and value proposition
        
        ## 2. Fundamental Concepts & Theoretical Foundation (1200+ words)
        - Core definitions and terminology with detailed explanations
        - Underlying scientific/engineering principles
        - Historical development and evolution
        - Relationship to broader field/industry context
        - Mathematical and scientific foundations
        - Key theories and models
        
        ## 3. Technical Specifications & Standards (1400+ words)
        - Detailed technical parameters and measurements
        - Performance characteristics and capabilities
        - Industry standards and regulatory requirements
        - Equipment specifications and configurations
        - Compliance requirements and certifications
        - Quality assurance and testing procedures
        
        ## 4. Operational Procedures & Implementation (1600+ words)
        - Step-by-step operational processes with detailed instructions
        - Setup, configuration, and commissioning procedures
        - Standard operating procedures (SOPs)
        - Quality control and verification methods
        - Performance monitoring and optimization
        - Integration with existing systems
        
        ## 5. Safety Protocols & Risk Management (900+ words)
        - Comprehensive safety guidelines and procedures
        - Risk assessment and hazard identification
        - Personal protective equipment (PPE) requirements
        - Emergency response procedures
        - Regulatory compliance and safety standards
        - Incident reporting and investigation
        
        ## 6. Maintenance & Troubleshooting Guide (1100+ words)
        - Preventive maintenance schedules and procedures
        - Common problems, symptoms, and root causes
        - Diagnostic procedures and tools
        - Step-by-step troubleshooting methodologies
        - Corrective actions and solutions
        - Maintenance cost analysis and optimization
        
        ## 7. Case Studies & Real-World Applications (1000+ words)
        - Industry implementation examples and success stories
        - Comparative analysis of different approaches
        - Lessons learned and best practices
        - Performance benchmarks and metrics
        - Economic and environmental considerations
        - ROI analysis and business cases
        
        ## 8. Advanced Topics & Future Developments (800+ words)
        - Emerging technologies and innovations
        - Advanced operational techniques
        - Research and development trends
        - Future market projections and opportunities
        - Integration with other technologies
        - Technology roadmaps and evolution
        
        ## 9. Regulatory Compliance & Documentation (600+ words)
        - Applicable regulations and standards
        - Documentation requirements
        - Audit and inspection procedures
        - Record keeping and reporting
        - Certification processes
        - Legal and compliance considerations
        
        ## 10. Additional Resources & References (500+ words)
        - Professional organizations and associations
        - Technical standards and guidelines
        - Training and certification programs
        - Recommended reading and resources
        - Contact information for experts and vendors
        - Online resources and databases
        
        QUALITY REQUIREMENTS:
        - Minimum 9000 words total across all sections
        - Each section must meet or exceed its minimum word count
        - Include specific technical data, numbers, and measurements
        - Provide detailed step-by-step procedures with examples
        - Include real-world examples and practical applications
        - Maintain professional technical writing style with clear explanations
        - Address ALL identified gaps and enhancement opportunities
        - Incorporate ALL recommended additional content
        - Use bullet points, numbered lists, and subheadings for clarity
        - Include technical specifications, standards, and best practices
        
        CONTENT DEPTH REQUIREMENTS:
        - Each major point should be expanded with detailed explanations
        - Include practical examples and case studies where applicable
        - Provide implementation guidance and actionable steps
        - Add technical context and background information
        - Include performance metrics, benchmarks, and evaluation criteria
        
        Generate the most comprehensive, detailed, and practical handout possible using all available information.
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
