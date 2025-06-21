"""
Main routes for serving the frontend
"""

from flask import render_template, send_from_directory, request, redirect, url_for, jsonify, Blueprint
import os
from app.services.rag_manager import get_rag_manager

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('index.html')

@main.route('/health')
def health_check():
    """Health check endpoint."""
    return {'status': 'healthy', 'service': 'WhiteLabelRAG'}, 200

@main.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return send_from_directory(static_dir, filename)

@main.route("/documents")
def documents():
    # Replace with actual document retrieval logic
    documents = [
        {"id": 1, "name": "Sample.pdf", "type": "pdf", "size": 123456, "uploaded": "2024-06-01", "source": "upload"},
        # ...more docs...
    ]
    return render_template("documents.html", documents=documents)

@main.route("/documents/open/<int:doc_id>")
def open_document(doc_id):
    # Implement document open logic
    return f"Open document {doc_id}"

@main.route("/documents/edit/<int:doc_id>")
def edit_document(doc_id):
    # Implement document edit logic
    return f"Edit document {doc_id}"

@main.route("/documents/delete/<int:doc_id>", methods=["POST"])
def delete_document(doc_id):
    # Implement document delete logic
    return redirect(url_for("main.documents"))

@main.route("/assistants")
def assistants():
    # Replace with actual assistant status/task retrieval logic
    assistants = [
        {"id": 1, "name": "Concierge", "type": "Orchestrator", "status": "online", "current_task": "Monitoring chat"},
        {"id": 2, "name": "SearchAgent", "type": "Search", "status": "online", "current_task": None},
        # ...more assistants...
    ]
    return render_template("assistants.html", assistants=assistants)

@main.route("/assistants/chat/<int:assistant_id>", methods=["POST"])
def assistant_chat(assistant_id):
    # Implement mini chat logic with specific assistant
    data = request.get_json()
    message = data.get("message", "")
    # For demo, echo back
    return jsonify({"reply": f"Echo from assistant {assistant_id}: {message}"})

@main.route("/api/decompose", methods=["POST"])
def decompose():
    try:
        data = request.get_json()
        query = data.get('message', '')
        rag = get_rag_manager()
        result = rag.query_documents(query)
        return jsonify({'response': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 200

@main.route("/api/query", methods=["POST"])
def query():
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = int(data.get('top_k', 3))
        rag = get_rag_manager()
        result = rag.query_documents(query, n_results=top_k)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'results': [], 'error': str(e)}), 200

@main.route("/health")
def health():
    rag = get_rag_manager()
    assistants = [
        {"name": "Concierge", "status": "online", "current_task": "Monitoring chat"},
        {"name": "SearchAgent", "status": "online", "current_task": None},
    ]
    tasks = [
        {"id": 1, "description": "Summarize uploaded file", "progress": "complete"},
        {"id": 2, "description": "Answer user query", "progress": "in_progress"},
    ]
    return jsonify({
        "status": "ok",
        "assistants": assistants,
        "tasks": tasks
    }), 200

# 404 error handler
@main.app_errorhandler(404)
def not_found(e):
    return render_template("404.html", error=str(e)), 404