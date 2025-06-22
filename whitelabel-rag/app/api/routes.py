"""
API routes for WhiteLabelRAG
"""

import os
import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse, FileResponse
