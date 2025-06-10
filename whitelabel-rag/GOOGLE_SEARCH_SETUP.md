# Google Custom Search Integration Guide

This guide explains how to set up and test the Google Custom Search integration for WhiteLabelRAG.

## 1. Prerequisites

- Google account
- WhiteLabelRAG application set up and running

## 2. Setting Up Google Custom Search

### 2.1 Create a Custom Search Engine

1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/about/)
2. Click "Get Started" to create a new search engine
3. Configure your search engine:
   - Name your search engine (e.g., "WhiteLabelRAG Internet Search")
   - Choose what to search:
     - Option 1: "Search the entire web" (recommended)
     - Option 2: Specify specific sites to search
   - Language settings: Choose your preferred languages
   - Click "Create"
4. On the next page, find your "Search engine ID" (cx) - it will look like: `012345678901234567890:abcdefghijk`
5. Copy this ID for later use

### 2.2 Get a Google API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Library"
4. Search for "Custom Search API" and select it
5. Click "Enable" to enable the API for your project
6. Navigate to "APIs & Services" > "Credentials"
7. Click "Create Credentials" > "API key"
8. Copy the generated API key
9. (Optional but recommended) Restrict the API key to only the Custom Search API

## 3. Configure WhiteLabelRAG

### 3.1 Set Environment Variables

Add the following to your `.env` file:

```
GOOGLE_API_KEY=your_google_api_key_here
INTERNET_SEARCH_ENGINE_ID=your_search_engine_id_here
```

### 3.2 Test the Configuration

Run the provided test script to verify that your configuration works correctly:

```bash
# Windows
scripts\test_google_search.bat

# Linux/Mac
bash scripts/test_internet_search.py

# Options:
# --direct-only   Test only the direct API call (not the app integration)
# --app-only      Test only the app integration (not the direct API call)
```

The test will:
1. Verify your API key and Search Engine ID are correctly set up
2. Make a direct call to the Google Custom Search API
3. Test the integration through the WhiteLabelRAG application API

## 4. Usage

When configured correctly, the WhiteLabelRAG application will automatically fall back to internet search when:

1. The document search returns no results
2. The document search returns low-confidence results
3. The query explicitly requests internet search with the parameter `use_internet_search=true`

### 4.1 Example API Call

```python
import requests

response = requests.post(
    "http://localhost:5000/api/query",
    json={
        "query": "latest AI developments",
        "top_k": 3,
        "use_internet_search": True  # Force internet search
    }
)

result = response.json()
print(result)
```

## 5. Troubleshooting

### 5.1 API Key Issues

- Ensure the API key is correctly copied without extra spaces
- Verify the API key has access to the Custom Search API
- Check usage quotas in Google Cloud Console

### 5.2 Search Engine ID Issues

- Ensure the Search Engine ID is correctly copied
- Verify the search engine is set up to search the web or relevant sites

### 5.3 API Quotas

The Google Custom Search API has the following quotas:
- 100 search queries per day for free
- For more queries, billing must be enabled on your Google Cloud project

## 6. Further Customization

You can customize your search engine settings at any time by returning to the [Programmable Search Engine Control Panel](https://programmablesearchengine.google.com/controlpanel/all).

---

For additional help, refer to the [Google Custom Search JSON API documentation](https://developers.google.com/custom-search/v1/overview).
