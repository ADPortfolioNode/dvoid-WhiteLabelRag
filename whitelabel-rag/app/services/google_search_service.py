import os
import requests

class GoogleSearchService:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_SEARCH_API_KEY")
        self.cse_id = os.environ.get("GOOGLE_CSE_ID")

    def search(self, query, num_results=3):
        if not self.api_key or not self.cse_id:
            # Placeholder: In production, raise or log error
            return [{"title": "No API key configured", "link": "", "snippet": "Google Search API key not set."}]
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": num_results,
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                })
            return results
        except Exception as e:
            return [{"title": "Google Search Error", "link": "", "snippet": str(e)}]
