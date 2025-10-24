from .base_agent import BaseAgent
from typing import Dict, Any, List

class TopicAnalyzerAgent(BaseAgent):
    def __init__(self, api_client, vector_store):
        super().__init__(api_client, vector_store, "TopicAnalyzer")
        
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze topic depth and identify content gaps"""
        topic = input_data.get('topic')
        vector_content = input_data.get('vector_content', '')
        google_content = input_data.get('google_content', {})
        
        # Combine content for analysis
        extracted_content = vector_content if isinstance(vector_content, str) else str(vector_content)
        content_categories = google_content if isinstance(google_content, dict) else {}
        
        # Calculate word counts safely
        content_word_count = len(extracted_content.split()) if extracted_content else 0
        category_word_counts = []
        for cat, content in content_categories.items():
            if isinstance(content, str):
                category_word_counts.append((cat, len(content.split())))
            else:
                category_word_counts.append((cat, len(str(content).split())))
        
        analysis_prompt = f"""
        You are a technical curriculum analyst. Analyze the extracted content for '{topic}' and provide comprehensive analysis.
        
        Current Content Analysis:
        - Total word count: {content_word_count} words
        - Categories covered: {list(content_categories.keys())}
        - Content per category: {category_word_counts}
        
        Perform detailed analysis in these areas:
        
        ## 1. CONTENT DEPTH ANALYSIS
        For each major category, assess:
        - Current detail level (Insufficient/Adequate/Comprehensive)
        - Technical accuracy and completeness
        - Missing technical specifications or parameters
        - Gaps in procedural information
        - Absence of industry standards or regulations
        
        ## 2. KNOWLEDGE GAPS IDENTIFICATION
        Identify specific missing content:
        - Essential concepts not adequately covered
        - Missing practical implementation details
        - Absent safety considerations or protocols
        - Lack of real-world examples or case studies
        - Missing troubleshooting scenarios
        - Inadequate maintenance procedures
        
        ## 3. ENHANCEMENT OPPORTUNITIES
        For each identified gap, provide specific recommendations:
        - Additional technical details needed (minimum 200 words each)
        - More comprehensive procedures required
        - Industry best practices to incorporate
        - Advanced topics that should be included
        - Comparative analysis opportunities
        
        ## 4. CONTENT EXPANSION PLAN
        Create a structured plan for content enhancement:
        - Priority levels (Critical/High/Medium/Low)
        - Expected word count increases per section
        - Specific subtopics to research and add
        - Advanced concepts to incorporate
        - Industry case studies to include
        
        ## 5. RECOMMENDED ADDITIONAL SECTIONS
        Suggest new sections that would enhance the handout:
        - Advanced operational techniques
        - Emerging technologies and trends
        - Regulatory compliance details
        - Performance optimization strategies
        - Future developments and research directions
        
        Current extracted content preview: {extracted_content[:3000]}...
        
        Generate comprehensive analysis with specific, actionable recommendations for significant content enhancement.
        Target: Identify opportunities to expand content by 100-150%.
        """
        
        analysis_result = self.api_client.generate_response(analysis_prompt)
        
        # Parse the analysis results
        content_gaps = self._identify_gaps(analysis_result)
        enhancement_suggestions = self._get_enhancements(analysis_result)
        expansion_plan = self._extract_expansion_plan(analysis_result)
        recommended_sections = self._extract_recommended_sections(analysis_result)
        
        return self.log_execution(
            f"Topic analysis for: {topic}",
            {
                'topic': topic,
                'analysis_result': analysis_result,
                'identified_gaps': content_gaps,
                'content_gaps': content_gaps,
                'enhancement_suggestions': enhancement_suggestions,
                'expansion_plan': expansion_plan,
                'recommended_sections': recommended_sections,
                'analysis_word_count': len(analysis_result.split()),
                'identified_gaps_count': len(content_gaps),
                'enhancement_opportunities_count': len(enhancement_suggestions)
            }
        )
    
    def _identify_gaps(self, analysis: str) -> List[Dict[str, str]]:
        """Extract identified content gaps with details"""
        gaps = []
        lines = analysis.split('\n')
        
        in_gaps_section = False
        current_gap = None
        
        for line in lines:
            if 'KNOWLEDGE GAPS' in line.upper():
                in_gaps_section = True
                continue
            elif line.startswith('##') and in_gaps_section:
                in_gaps_section = False
                break
            elif in_gaps_section and line.strip().startswith('-'):
                gap_text = line.strip('- ').strip()
                if gap_text:
                    gaps.append({
                        'gap_description': gap_text,
                        'priority': 'High',  # Default priority
                        'estimated_words': 200  # Default word count
                    })
        
        return gaps
    
    def _get_enhancements(self, analysis: str) -> List[Dict[str, str]]:
        """Extract enhancement suggestions with priorities"""
        enhancements = []
        lines = analysis.split('\n')
        
        in_enhancement_section = False
        
        for line in lines:
            if 'ENHANCEMENT OPPORTUNITIES' in line.upper():
                in_enhancement_section = True
                continue
            elif line.startswith('##') and in_enhancement_section:
                in_enhancement_section = False
                break
            elif in_enhancement_section and line.strip().startswith('-'):
                enhancement_text = line.strip('- ').strip()
                if enhancement_text:
                    enhancements.append({
                        'enhancement_description': enhancement_text,
                        'impact': 'High',
                        'implementation_complexity': 'Medium'
                    })
        
        return enhancements
    
    def _extract_expansion_plan(self, analysis: str) -> Dict[str, Any]:
        """Extract the content expansion plan"""
        lines = analysis.split('\n')
        in_plan_section = False
        plan_content = []
        
        for line in lines:
            if 'CONTENT EXPANSION PLAN' in line.upper():
                in_plan_section = True
                continue
            elif line.startswith('##') and in_plan_section:
                break
            elif in_plan_section:
                plan_content.append(line)
        
        return {
            'plan_text': '\n'.join(plan_content),
            'estimated_expansion': '100-150%',
            'focus_areas': ['technical_specifications', 'procedures', 'case_studies', 'troubleshooting']
        }
    
    def _extract_recommended_sections(self, analysis: str) -> List[str]:
        """Extract recommended additional sections"""
        sections = []
        lines = analysis.split('\n')
        
        in_sections = False
        
        for line in lines:
            if 'RECOMMENDED ADDITIONAL SECTIONS' in line.upper():
                in_sections = True
                continue
            elif line.startswith('##') and in_sections:
                break
            elif in_sections and line.strip().startswith('-'):
                section_text = line.strip('- ').strip()
                if section_text:
                    sections.append(section_text)
        
        return sections
