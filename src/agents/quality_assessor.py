from .base_agent import BaseAgent
from typing import Dict, Any, List

class QualityAssessorAgent(BaseAgent):
    def __init__(self, api_client, vector_store):
        super().__init__(api_client, vector_store, "QualityAssessor")
        
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess handout quality and suggest improvements"""
        topic = input_data.get('topic')
        handout_content = input_data.get('handout_content', '')
        word_count = input_data.get('word_count', 0)
        sections_count = input_data.get('sections_count', 0)
        
        assessment_prompt = f"""
        You are a technical documentation quality assessor. Evaluate this handout for '{topic}' comprehensively.
        
        HANDOUT STATISTICS:
        - Word count: {word_count}
        - Sections: {sections_count}
        - Topic: {topic}
        
        CONTENT LENGTH REQUIREMENTS:
        - Minimum acceptable: 6,000 words (basic quality)
        - Good quality: 8,000+ words 
        - Excellent quality: 10,000+ words
        - Current status: {"MEETS MINIMUM" if word_count >= 6000 else "BELOW MINIMUM" if word_count >= 8000 else "EXCELLENT LENGTH" if word_count >= 10000 else "TOO SHORT"}
        
        Evaluate and provide detailed scores (1-10) for each criterion:
        
        ## 1. CONTENT QUALITY & TECHNICAL ACCURACY (Score: X/10)
        Assess:
        - Technical accuracy and precision
        - Depth of technical detail and explanations
        - Completeness of information across all sections
        - Use of specific data, numbers, and measurements
        - Industry standard compliance and best practices
        - Sufficient detail level for professional use
        
        ## 2. STRUCTURE & ORGANIZATION (Score: X/10)
        Evaluate:
        - Logical flow and progression between sections
        - Clear section organization with comprehensive coverage
        - Appropriate level of detail per section (aim for 800+ words per major section)
        - Effective use of headings, subheadings, and bullet points
        - Readability and navigation with detailed explanations
        
        ## 3. PRACTICAL VALUE & APPLICABILITY (Score: X/10)
        Analyze:
        - Real-world applicability with detailed procedures
        - Actionable procedures and step-by-step guidelines
        - Practical examples, case studies, and implementation guides
        - Professional utility for target audience
        - Implementation guidance quality with specific instructions
        
        ## 4. COMPREHENSIVENESS & COVERAGE (Score: X/10)
        Review (DEDUCT POINTS FOR INSUFFICIENT CONTENT LENGTH):
        - Word count adequacy: {10 if word_count >= 10000 else 8 if word_count >= 8000 else 6 if word_count >= 6000 else 3}/10
        - Coverage of all essential topics with sufficient depth
        - Coverage of all essential topics
        - Adequate depth in each area
        - Inclusion of safety and compliance aspects
        - Troubleshooting and maintenance coverage
        - Advanced topics and future considerations
        
        ## 5. PROFESSIONAL PRESENTATION (Score: X/10)
        Assess:
        - Professional writing style and tone
        - Consistency in formatting and structure
        - Appropriate technical language usage
        - Clear and concise explanations
        - Overall document presentation quality
        
        ## DETAILED IMPROVEMENT RECOMMENDATIONS
        For any score below 8, provide SPECIFIC improvements:
        
        ### Content Enhancements Needed:
        - Specific sections requiring more technical detail
        - Missing technical specifications or parameters
        - Additional procedures or methodologies needed
        - More case studies or examples required
        
        ### Structural Improvements:
        - Sections that need reorganization
        - Areas requiring better flow or transitions
        - Subsections that should be added or expanded
        - Formatting or presentation improvements
        
        ### Additional Content Suggestions:
        - New sections or topics to include
        - Enhanced safety or compliance content
        - More detailed troubleshooting information
        - Additional references or resources
        
        ## OVERALL ASSESSMENT SUMMARY
        - Overall Quality Score: X/10 (average of all scores)
        - Readiness Level: (Ready for Use/Needs Minor Improvements/Requires Major Revisions)
        - Key Strengths: [List 3-5 main strengths]
        - Priority Improvements: [List 3-5 most critical improvements]
        
        HANDOUT CONTENT TO ASSESS (first 4000 characters):
        {handout_content[:4000]}...
        
        Provide thorough, specific assessment with actionable improvement recommendations.
        """
        
        assessment_result = self.api_client.generate_response(assessment_prompt)
        
        # Parse assessment results
        quality_scores = self._extract_scores(assessment_result)
        improvement_suggestions = self._extract_improvements(assessment_result)
        readiness_level = self._extract_readiness_level(assessment_result)
        strengths = self._extract_strengths(assessment_result)
        priority_improvements = self._extract_priority_improvements(assessment_result)
        
        # Calculate word count from handout content
        handout_word_count = len(handout_content.split()) if handout_content else 0
        
        return self.log_execution(
            f"Quality assessment for: {topic}",
            {
                'topic': topic,
                'assessment_result': assessment_result,
                'quality_scores': quality_scores,
                'quality_score': sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0,
                'word_count': handout_word_count,
                'improvement_suggestions': improvement_suggestions,
                'readiness_level': readiness_level,
                'strengths': strengths,
                'priority_improvements': priority_improvements,
                'assessment_word_count': len(assessment_result.split()),
                'recommendations_count': len(improvement_suggestions)
            }
        )
    
    def _extract_scores(self, assessment: str) -> Dict[str, float]:
        """Extract quality scores from assessment"""
        scores = {}
        lines = assessment.split('\n')
        
        score_categories = {
            'content_quality': ['CONTENT QUALITY', 'TECHNICAL ACCURACY'],
            'structure': ['STRUCTURE', 'ORGANIZATION'],
            'practical_value': ['PRACTICAL VALUE', 'APPLICABILITY'],
            'comprehensiveness': ['COMPREHENSIVENESS', 'COVERAGE'],
            'presentation': ['PROFESSIONAL PRESENTATION']
        }
        
        for line in lines:
            if 'Score:' in line:
                for category, keywords in score_categories.items():
                    if any(keyword in line.upper() for keyword in keywords):
                        try:
                            # Extract score from format "Score: X/10"
                            score_part = line.split('Score:')[1].split('/')[0].strip()
                            scores[category] = float(score_part)
                        except (IndexError, ValueError):
                            scores[category] = 7.0  # Default score
                        break
        
        # Ensure all categories have scores
        for category in score_categories.keys():
            if category not in scores:
                scores[category] = 7.0
        
        return scores
    
    def _extract_improvements(self, assessment: str) -> List[Dict[str, str]]:
        """Extract improvement suggestions from assessment"""
        improvements = []
        lines = assessment.split('\n')
        
        in_improvements_section = False
        current_category = None
        
        for line in lines:
            if 'IMPROVEMENT RECOMMENDATIONS' in line.upper():
                in_improvements_section = True
                continue
            elif 'OVERALL ASSESSMENT' in line.upper():
                in_improvements_section = False
                break
            elif in_improvements_section:
                if line.startswith('###'):
                    current_category = line.strip('#').strip()
                elif line.strip().startswith('-') and current_category:
                    improvement_text = line.strip('- ').strip()
                    if improvement_text:
                        improvements.append({
                            'category': current_category,
                            'improvement': improvement_text,
                            'priority': 'Medium'  # Default priority
                        })
        
        return improvements
    
    def _extract_readiness_level(self, assessment: str) -> str:
        """Extract readiness level from assessment"""
        lines = assessment.split('\n')
        
        for line in lines:
            if 'Readiness Level:' in line:
                return line.split('Readiness Level:')[1].strip()
        
        return "Assessment pending"
    
    def _extract_strengths(self, assessment: str) -> List[str]:
        """Extract key strengths from assessment"""
        strengths = []
        lines = assessment.split('\n')
        
        in_strengths = False
        
        for line in lines:
            if 'Key Strengths:' in line:
                in_strengths = True
                # Check if strengths are on the same line
                if '[' in line:
                    strengths_text = line.split('[')[1].split(']')[0]
                    strengths = [s.strip() for s in strengths_text.split(',')]
                    break
                continue
            elif in_strengths and line.strip().startswith('-'):
                strength = line.strip('- ').strip()
                if strength:
                    strengths.append(strength)
            elif in_strengths and 'Priority Improvements:' in line:
                break
        
        return strengths
    
    def _extract_priority_improvements(self, assessment: str) -> List[str]:
        """Extract priority improvements from assessment"""
        improvements = []
        lines = assessment.split('\n')
        
        in_priority = False
        
        for line in lines:
            if 'Priority Improvements:' in line:
                in_priority = True
                # Check if improvements are on the same line
                if '[' in line:
                    improvements_text = line.split('[')[1].split(']')[0]
                    improvements = [i.strip() for i in improvements_text.split(',')]
                    break
                continue
            elif in_priority and line.strip().startswith('-'):
                improvement = line.strip('- ').strip()
                if improvement:
                    improvements.append(improvement)
            elif in_priority and line.strip() == '':
                break
        
        return improvements
