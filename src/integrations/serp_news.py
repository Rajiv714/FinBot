"""
Google News integration using SERPAPI
Fetches top news articles related to financial topics
"""
import os
from typing import List, Dict, Any
from serpapi import GoogleSearch


def fetch_news(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch top news articles from Google News using SERPAPI.
    
    Args:
        query: Search query (e.g., "personal finance", "mutual funds")
        max_results: Maximum number of results (default: 5)
        
    Returns:
        List of news articles with title, link, source, date, snippet
    """
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            print("⚠️  SERPAPI_API_KEY not found in environment")
            return []
        
        params = {
            "engine": "google_news",
            "q": f"{query} finance investment",
            "api_key": api_key,
            "num": max_results,
            "gl": "in",  # India
            "hl": "en"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Check for API errors
        if "error" in results:
            print(f"⚠️  SERPAPI Error: {results['error']}")
            print("📝 Get your free API key at: https://serpapi.com/manage-api-key")
            print("   Then update SERPAPI_API_KEY in .env file")
            return []
        
        news_results = []
        if "news_results" in results:
            for item in results["news_results"][:max_results]:
                news_results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "source": item.get("source", {}).get("name", "Unknown"),
                    "date": item.get("date", ""),
                    "snippet": item.get("snippet", "")
                })
        
        return news_results
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []
