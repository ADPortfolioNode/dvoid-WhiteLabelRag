"""
API Router for WhiteLabelRAG
"""

from fastapi import APIRouter

api_bp = APIRouter()

from . import routes
