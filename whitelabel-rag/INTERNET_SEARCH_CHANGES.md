# Internet Search Integration Summary

## Overview

The WhiteLabelRAG application has been updated to use Google Custom Search API for internet search functionality. This feature allows the application to fall back to internet search when the document-based RAG system doesn't contain the answer to a user's query.

## Changes Made

1. **Configuration Updates**
   - Updated `app/config.py` to use `GOOGLE_API_KEY` environment variable
   - Added proper configuration in docker-compose files
   - Created `.env.example` with Google API key and Search Engine ID placeholders

2. **API Enhancements**
   - Added `force_internet_search` parameter to `query_documents` method in RAG Manager
   - Updated `/api/query` endpoint to accept `use_internet_search` parameter

3. **Documentation**
   - Created comprehensive `GOOGLE_SEARCH_SETUP.md` guide
   - Updated `README.md` with internet search setup instructions
   - Updated `DEPLOYMENT.md` to include Google API key configuration
   - Added internet search to technology stack in `INSTRUCTIONS.md`

4. **Testing Tools**
   - Created `test_internet_search.py` script for testing Google API integration
   - Added batch script `test_google_search.bat` for Windows users
   - Added shell script `test_google_search.sh` for Linux/Mac users

## How It Works

1. When a user sends a query to the `/api/query` endpoint, the application first tries to find an answer in the document store.
2. If no relevant documents are found or if `use_internet_search=true` is specified, the application falls back to internet search.
3. The internet search is performed using the Google Custom Search API with the provided `GOOGLE_API_KEY` and `INTERNET_SEARCH_ENGINE_ID`.
4. The results from both document search and internet search (if performed) are returned to the user.

## Testing

To test the integration:

```bash
# Windows
scripts\test_google_search.bat

# Linux/Mac
bash scripts/test_google_search.sh
```

## Requirements

- Google Account
- Google Custom Search Engine ID
- Google API Key with access to Custom Search API
