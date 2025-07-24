from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

import os
import logging

logger = logging.getLogger(__name__)

from app.api.routes import api_bp as api_router

def create_app():
    from fastapi.staticfiles import StaticFiles
    from app.frontend_router import router as frontend_router
    import os

    app = FastAPI(title="WhiteLabelRAG API", version="1.0.0")

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), 'static')), name="static")

    # Include old frontend routes
    app.include_router(frontend_router)

    @app.get("/health")
    async def health():
        try:
            chroma_status = "unknown"
            try:
                from app.services.chroma_service import get_chroma_service_instance
                chroma_service = get_chroma_service_instance()
                chroma_status = "healthy"
            except Exception as e:
                logger.warning(f"Error accessing ChromaDB: {str(e)}")
                chroma_status = "error"

            return JSONResponse(content={
                "status": "online",
                "version": "1.0.0",
                "environment": os.environ.get("FLASK_ENV", "production"),
                "services": {
                    "chromadb": chroma_status,
                    "api": "online"
                }
            })
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

    app.include_router(api_router, prefix="/api")

    logger.info("FastAPI app initialized successfully")
    return app
