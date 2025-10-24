from .base_agent import BaseAgent
from typing import Dict, Any, List
import os
from serpapi import GoogleSearch

class GoogleSearchAgent(BaseAgent):
    """Agent specialized in extracting relevant data from Google search using SERP API"""
    
    def __init__(self, api_client, vector_store):
        super().__init__(api_client, vector_store, "GoogleSearchAgent")
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        if not self.serpapi_key:
            raise ValueError("SERPAPI_API_KEY not found in environment variables")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search Google for relevant information about the topic"""
        topic = input_data.get('topic')
        search_depth = input_data.get('search_depth', 'comprehensive')  # basic, standard, comprehensive
        
        # Define search strategies based on depth
        search_queries = self._generate_search_queries(topic, search_depth)
        
        print(f"   Searching Google with {len(search_queries)} targeted queries...")
        
        # Collect search results
        all_results = []
        for i, query in enumerate(search_queries, 1):
            print(f"   Query {i}/{len(search_queries)}: {query}")
            results = self._perform_search(query)
            all_results.extend(results)
        
        # Process and enhance search results
        processed_results = self._process_search_results(all_results, topic)
        
        # Extract structured information
        structured_content = self._extract_structured_content(processed_results, topic)
        
        return self.log_execution(
            f"Google search for: {topic}",
            {
                'topic': topic,
                'search_queries': search_queries,
                'raw_results_count': len(all_results),
                'processed_results': processed_results,
                'structured_content': structured_content,
                'content_categories': {
                    'technical_specifications': len([r for r in processed_results if 'specification' in r.get('category', '').lower()]),
                    'safety_procedures': len([r for r in processed_results if 'safety' in r.get('category', '').lower()]),
                    'case_studies': len([r for r in processed_results if 'case' in r.get('category', '').lower()]),
                    'standards_regulations': len([r for r in processed_results if 'standard' in r.get('category', '').lower()]),
                    'troubleshooting': len([r for r in processed_results if 'troubleshoot' in r.get('category', '').lower()])
                }
            }
        )
    
    def _generate_search_queries(self, topic: str, search_depth: str) -> List[str]:
        """Generate targeted search queries based on topic and depth"""
        
        base_queries = [
            f"{topic} technical specifications standards",
            f"{topic} safety procedures protocols",
            f"{topic} operation maintenance guidelines",
            f"{topic} troubleshooting common issues",
            f"{topic} industry applications case studies"
        ]
        
        if search_depth == 'comprehensive':
            # Limit to total of 5 queries for comprehensive search
            return base_queries[:5]
        elif search_depth == 'standard':
            return base_queries + [
                f"{topic} certification requirements",
                f"{topic} performance metrics",
                f"{topic} installation procedures"
            ]
        else:  # basic
            return base_queries[:3]
    
    def _perform_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform a single Google search and return results"""
        try:
            search_params = {
                "api_key": self.serpapi_key,
                "engine": "google",
                "q": query,
                "num": 10,  # Get top 10 results per query
                "hl": "en",
                "gl": "us"
            }
            
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            search_results = []
            if "organic_results" in results:
                for result in results["organic_results"]:
                    search_results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('snippet', ''),
                        'link': result.get('link', ''),
                        'query': query,
                        'source': 'google_organic'
                    })
            
            # Also include featured snippets if available
            if "answer_box" in results:
                answer_box = results["answer_box"]
                search_results.append({
                    'title': f"Featured Answer: {answer_box.get('title', '')}",
                    'snippet': answer_box.get('snippet', '') or answer_box.get('answer', ''),
                    'link': answer_box.get('link', ''),
                    'query': query,
                    'source': 'google_featured'
                })
            
            return search_results
            
        except Exception as e:
            print(f" Search error for query '{query}': {str(e)}")
            return []
    
    def _process_search_results(self, results: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        """Process and categorize search results"""
        processed = []
        
        for result in results:
            # Skip if no useful content
            if not result.get('snippet') or len(result.get('snippet', '')) < 50:
                continue
            
            # Categorize result based on content
            category = self._categorize_result(result, topic)
            
            # Clean and enhance snippet
            cleaned_snippet = self._clean_snippet(result['snippet'])
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance(result, topic)
            
            processed.append({
                'title': result['title'],
                'content': cleaned_snippet,
                'source_url': result['link'],
                'original_query': result['query'],
                'category': category,
                'relevance_score': relevance_score,
                'source_type': result['source']
            })
        
        # Sort by relevance and remove duplicates
        processed = sorted(processed, key=lambda x: x['relevance_score'], reverse=True)
        processed = self._remove_duplicates(processed)
        
        return processed[:30]  # Keep top 30 most relevant results
    
    def _categorize_result(self, result: Dict[str, Any], topic: str) -> str:
        """Categorize search result based on content"""
        content = (result.get('title', '') + ' ' + result.get('snippet', '')).lower()
        
        categories = {
            'technical_specifications': ['specification', 'parameter', 'measurement', 'dimension', 'capacity', 'performance'],
            'safety_procedures': ['safety', 'hazard', 'risk', 'protection', 'emergency', 'protocol'],
            'maintenance_troubleshooting': ['maintenance', 'repair', 'troubleshoot', 'diagnostic', 'fix', 'service'],
            'standards_regulations': ['standard', 'regulation', 'compliance', 'certification', 'code', 'requirement'],
            'case_studies': ['case study', 'example', 'implementation', 'project', 'application', 'success'],
            'installation_setup': ['installation', 'setup', 'configuration', 'assembly', 'deployment'],
            'cost_benefits': ['cost', 'price', 'benefit', 'ROI', 'economic', 'financial']
        }
        
        for category, keywords in categories.items():
            if any(keyword in content for keyword in keywords):
                return category
        
        return 'general_information'
    
    def _clean_snippet(self, snippet: str) -> str:
        """Clean and normalize snippet text"""
        import re
        
        # Remove excessive whitespace
        snippet = re.sub(r'\s+', ' ', snippet)
        
        # Remove common artifacts
        snippet = re.sub(r'^\d+\s*[.)\-]\s*', '', snippet)  # Remove numbering
        snippet = re.sub(r'\s*\.\.\.\s*$', '', snippet)     # Remove trailing ellipsis
        
        return snippet.strip()
    
    def _calculate_relevance(self, result: Dict[str, Any], topic: str) -> float:
        """Calculate relevance score for a result"""
        content = (result.get('title', '') + ' ' + result.get('snippet', '')).lower()
        topic_words = topic.lower().split()
        
        # Base score
        score = 0.5
        
        # Boost for topic words in title
        title_lower = result.get('title', '').lower()
        title_matches = sum(1 for word in topic_words if word in title_lower)
        score += (title_matches / len(topic_words)) * 0.3
        
        # Boost for topic words in content
        content_matches = sum(1 for word in topic_words if word in content)
        score += (content_matches / len(topic_words)) * 0.2
        
        # Boost for featured snippets
        if result.get('source') == 'google_featured':
            score += 0.2
        
        # Boost for technical content indicators
        tech_indicators = ['specification', 'standard', 'protocol', 'procedure', 'parameter']
        if any(indicator in content for indicator in tech_indicators):
            score += 0.1
        
        return min(score, 1.0)
    
    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on content similarity"""
        unique_results = []
        seen_content = set()
        
        for result in results:
            # Create a normalized content signature
            content_signature = ' '.join(sorted(result['content'].lower().split()[:10]))
            
            if content_signature not in seen_content:
                seen_content.add(content_signature)
                unique_results.append(result)
        
        return unique_results
    
    def _extract_structured_content(self, results: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
        """Extract and structure content by categories"""
        structured = {
            'technical_specifications': [],
            'safety_procedures': [],
            'maintenance_troubleshooting': [],
            'standards_regulations': [],
            'case_studies': [],
            'installation_setup': [],
            'cost_benefits': [],
            'general_information': []
        }
        
        for result in results:
            category = result['category']
            structured[category].append({
                'content': result['content'],
                'source': result['source_url'],
                'relevance': result['relevance_score']
            })
        
        # Summarize each category
        summary = {}
        for category, items in structured.items():
            if items:
                summary[category] = {
                    'count': len(items),
                    'top_content': [item['content'] for item in items[:3]],  # Top 3 most relevant
                    'total_relevance': sum(item['relevance'] for item in items)
                }
        
        return {
            'categorized_content': structured,
            'category_summary': summary,
            'total_results': len(results),
            'total_content_length': sum(len(result['content']) for result in results)
        }