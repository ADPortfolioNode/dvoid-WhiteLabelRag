#!/bin/bash
# Script to run ChromaDB FastAPI server

uvicorn app.chroma_api:app --host 0.0.0.0 --port 8000
