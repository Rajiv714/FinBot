"""
YouTube integration using SERPAPI
Fetches top YouTube videos related to financial topics
"""
import os
from typing import List, Dict, Any
from serpapi import GoogleSearch


def fetch_youtube_videos(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch top YouTube videos using SERPAPI.
    
    Args:
        query: Search query (e.g., "personal finance", "mutual funds")
        max_results: Maximum number of results (default: 5)
        
    Returns:
        List of videos with title, link, channel, thumbnail, duration
    """
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            print("⚠️  SERPAPI_API_KEY not found in environment")
            return []
        
        params = {
            "engine": "youtube",
            "search_query": f"{query} finance investment explained",
            "api_key": api_key,
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
        
        video_results = []
        if "video_results" in results:
            for item in results["video_results"][:max_results]:
                video_results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "channel": item.get("channel", {}).get("name", "Unknown"),
                    "thumbnail": item.get("thumbnail", {}).get("static", ""),
                    "duration": item.get("length", ""),
                    "views": item.get("views", "")
                })
        
        return video_results
        
    except Exception as e:
        print(f"Error fetching YouTube videos: {e}")
        return []
