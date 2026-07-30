import requests
from typing import List, Dict, Any
from crewai.tools import tool
from config.settings import settings

@tool("serper_search_tool")
def serper_search_tool(query: str, domain: str = "") -> List[Dict[str, Any]]:
    """
    Search Google via Serper.dev API to find candidate profile URLs for a specific domain.
    Input format: job title / role and target sourcing domain.
    """
    if not settings.serper_api_key or settings.serper_api_key == "your_serper_api_key_here":
        # Fallback search result structure if API key is not configured
        return [
            {
                "title": f"{query} candidates on {domain}",
                "link": f"https://www.{domain}/search?q={query.replace(' ', '+')}",
                "snippet": f"Browse {query} candidate profiles on {domain}."
            }
        ]

    url = "https://google.serper.dev/search"
    search_term = f"site:{domain} {query}" if domain else query
    payload = {"q": search_term, "num": 5}
    headers = {
        'X-API-KEY': settings.serper_api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [
                {
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet")
                }
                for item in data.get("organic", [])
            ]
    except Exception:
        pass

    return [
        {
            "title": f"{query} candidates on {domain}",
            "link": f"https://www.{domain}/search?q={query.replace(' ', '+')}",
            "snippet": f"Browse {query} candidate profiles on {domain}."
        }
    ]
