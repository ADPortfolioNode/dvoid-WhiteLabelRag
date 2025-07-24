from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/documents", response_class=HTMLResponse)
async def documents(request: Request):
    documents = [
        {"id": 1, "name": "Sample.pdf", "type": "pdf", "size": 123456, "uploaded": "2024-06-01", "source": "upload"},
        # Add more documents as needed
    ]
    return templates.TemplateResponse("documents.html", {"request": request, "documents": documents})

@router.get("/assistants", response_class=HTMLResponse)
async def assistants(request: Request):
    assistants = [
        {"id": 1, "name": "Concierge", "type": "Orchestrator", "status": "online", "current_task": "Monitoring chat"},
        {"id": 2, "name": "SearchAgent", "type": "Search", "status": "online", "current_task": None},
        # Add more assistants as needed
    ]
    return templates.TemplateResponse("assistants.html", {"request": request, "assistants": assistants})

@router.get("/health")
async def health():
    return {
        "status": "online",
        "version": "1.0.0",
        "environment": "production",
        "services": {
            "chromadb": "unknown",
            "api": "online"
        }
    }
