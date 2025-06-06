"""
Main routes for serving the frontend
"""

from flask import render_template, send_from_directory
from . import main_bp
import os

@main_bp.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('index.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint."""
    return {'status': 'healthy', 'service': 'WhiteLabelRAG'}, 200

@main_bp.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return send_from_directory(static_dir, filename)