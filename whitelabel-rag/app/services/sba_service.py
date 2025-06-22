import requests

class SBAService:
    """Service for accessing SBA.gov API endpoints."""

    BASE_URL = "https://api.sba.gov/"

    def get_resource(self, endpoint, params=None):
        """Generic GET request to SBA.gov API."""
        url = self.BASE_URL + endpoint.lstrip("/")
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def get_small_business_resources(self, query=None):
        """Fetch small business resources, optionally filtered by query."""
        params = {"q": query} if query else None
        return self.get_resource("resources", params=params)

    def get_grants(self, params=None):
        """Fetch grants information."""
        return self.get_resource("grants", params=params)
