"""
API routes for WhiteLabelRAG
"""

import os
import uuid
import logging
from datetime import datetime
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask import Blueprint
api_bp = Blueprint('api_routes', __name__)
from app.services.concierge import get_concierge_instance
from app.services.chroma_service import get_chroma_service_instance
from app.services.rag_manager import get_rag_manager
from app.services.document_processor import DocumentProcessor
from app.services.internet_search_agent import get_internet_search_agent_instance
from app.services.multimedia_agent import get_multimedia_agent_instance
from app.services.file_manager import get_file_manager_instance
from app.utils.file_utils import allowed_file


logger = logging.getLogger(__name__)

import difflib
import ast
import os

def extract_docstrings_and_comments(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        parsed = ast.parse(source)
        docstrings = []
        for node in ast.walk(parsed):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                docstring = ast.get_docstring(node)
                if docstring:
                    docstrings.append(docstring)
        # Extract comments (lines starting with #)
        comments = []
        for line in source.splitlines():
            line_strip = line.strip()
            if line_strip.startswith('#'):
                comments.append(line_strip.lstrip('#').strip())
        return "\n".join(docstrings + comments)
    except Exception:
        return ""

def get_all_py_files(root_dir):
    py_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                py_files.append(os.path.join(dirpath, filename))
    return py_files

@api_bp.route('/metrics/accuracy_regression', methods=['GET'])
def get_accuracy_regression():
    """Calculate and return accuracy and regression percentages."""
    try:
        instructions_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'INSTRUCTIONS.md'))
        with open(instructions_path, 'r', encoding='utf-8') as f:
            instructions_text = f.read()[:1000]  # Use first 1000 chars as summary
        
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'whitelabel-rag'))
        py_files = get_all_py_files(root_dir)
        texts = []
        for file in py_files:
            texts.append(extract_docstrings_and_comments(file))
        codebase_text = "\n".join(texts)
        
        similarity = difflib.SequenceMatcher(None, instructions_text, codebase_text).ratio()
        regression = 1 - similarity
        
        return jsonify({
            'accuracy_percent': round(similarity * 100, 2),
            'regression_percent': round(regression * 100, 2)
        })
    except Exception as e:
        logger.error(f"Error calculating accuracy and regression: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/decompose', methods=['POST'])
def decompose_task():
    """Decompose user message into steps or handle conversation."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message']
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Get Concierge instance and handle message
        concierge = get_concierge_instance()
        response = concierge.handle_message(message, session_id)
        
        return jsonify({
            'response': response,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error in decompose_task: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/execute', methods=['POST'])
def execute_task():
    """Execute a decomposed task step."""
    try:
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({'error': 'Task is required'}), 400
        
        task = data['task']
        retry = request.args.get('retry', 'false').lower() == 'true'
        
        # Get the appropriate agent based on suggested_agent_type
        agent_type = task.get('suggested_agent_type', 'SearchAgent')
        
        if agent_type == 'SearchAgent':
            from app.services.search_agent import get_search_agent_instance
            agent = get_search_agent_instance()
        elif agent_type == 'FileAgent':
            from app.services.file_agent import get_file_agent_instance
            agent = get_file_agent_instance()
        elif agent_type == 'FunctionAgent':
            from app.services.function_agent import get_function_agent_instance
            agent = get_function_agent_instance()
        else:
            return jsonify({'error': f'Unknown agent type: {agent_type}'}), 400
        
        # Execute the task
        result = agent.handle_message(task.get('instruction', ''))
        
        return jsonify({
            'step_number': task.get('step_number', 1),
            'status': 'completed' if not result.get('error') else 'failed',
            'result': result.get('text', ''),
            'agent': agent_type
        })
        
    except Exception as e:
        logger.error(f"Error in execute_task: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/validate', methods=['POST'])
def validate_result():
    """Validate a step result."""
    try:
        data = request.get_json()
        if not data or 'result' not in data or 'task' not in data:
            return jsonify({'error': 'Result and task are required'}), 400
        
        result = data['result']
        task = data['task']
        
        # Simple validation logic - can be enhanced with LLM-based validation
        confidence = 0.9 if len(result) > 10 else 0.5
        status = 'PASS' if confidence > 0.7 else 'FAIL'
        
        return jsonify({
            'status': status,
            'confidence': confidence,
            'feedback': 'Result validated successfully' if status == 'PASS' else 'Result needs improvement'
        })
        
    except Exception as e:
        logger.error(f"Error in validate_result: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tasks/<task_id>/results', methods=['GET'])
def get_task_results(task_id):
    """Get task results by ID."""
    try:
        # This would typically fetch from a database
        # For now, return a placeholder response
        return jsonify({
            'task_id': task_id,
            'status': 'completed',
            'steps': []
        })
        
    except Exception as e:
        logger.error(f"Error in get_task_results: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/files', methods=['GET'])
def list_files():
    """List uploaded documents."""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        upload_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), upload_folder)
        
        if not os.path.exists(upload_path):
            return jsonify({'files': []})
        
        files = []
        for filename in os.listdir(upload_path):
            if os.path.isfile(os.path.join(upload_path, filename)):
                files.append({
                    'id': filename,
                    'name': filename,
                    'size': os.path.getsize(os.path.join(upload_path, filename)),
                    'modified': datetime.fromtimestamp(
                        os.path.getmtime(os.path.join(upload_path, filename))
                    ).isoformat()
                })
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error in list_files: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/files', methods=['POST'])
def upload_file():
    """Upload a document."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        upload_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), upload_folder)
        
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/multimedia/upload', methods=['POST'])
def upload_multimedia():
    """Upload a multimedia file."""
    try:
        multimedia_agent = get_multimedia_agent_instance()
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        result = multimedia_agent.save_file(file)
        if result.get('error'):
            return jsonify({'error': result['text']}), 400
        
        return jsonify({
            'message': 'Multimedia file uploaded successfully',
            'filename': result.get('filename')
        })
    except Exception as e:
        logger.error(f"Error in upload_multimedia: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/file/summarize', methods=['POST'])
def summarize_file():
    """Summarize a document file content."""
    try:
        data = request.get_json()
        document_text = data.get('document_text')
        if not document_text:
            return jsonify({'error': 'No document_text provided'}), 400
        
        file_manager = get_file_manager_instance()
        summary_result = file_manager.summarize_document(document_text)
        
        if summary_result.get('success'):
            return jsonify({'summary': summary_result['summary']})
        else:
            return jsonify({'error': summary_result.get('error', 'Unknown error')}), 500
    except Exception as e:
        logger.error(f"Error in summarize_file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/multimedia/info/<filename>', methods=['GET'])
def multimedia_file_info(filename):
    """Get information about a multimedia file."""
    try:
        multimedia_agent = get_multimedia_agent_instance()
        if not multimedia_agent.is_supported_format(filename):
            return jsonify({'error': 'Unsupported file type'}), 400
        
        file_path = os.path.join(multimedia_agent.uploads_path, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        file_info = {
            'filename': filename,
            'size': os.path.getsize(file_path),
            'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }
        
        return jsonify({'file_info': file_info})
    except Exception as e:
        logger.error(f"Error in multimedia_file_info: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/documents/upload_and_ingest_document', methods=['POST'])
def upload_and_ingest_document():
    """Upload and ingest a document into the vector database."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        upload_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), upload_folder)
        
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        
        # Process and ingest the document
        processor = DocumentProcessor()
        rag_manager = get_rag_manager()
        
        # Extract text and create chunks
        chunks = processor.process_document(file_path)
        
        # Store in vector database
        for i, chunk in enumerate(chunks):
            rag_manager.store_document_chunk(
                content=chunk['content'],
                metadata={
                    'source': filename,
                    'chunk_id': i,
                    'total_chunks': len(chunks),
                    'file_path': file_path,
                    'timestamp': datetime.now().isoformat()
                }
            )
        
        return jsonify({
            'message': f'Document uploaded and ingested successfully. Created {len(chunks)} chunks.',
            'filename': filename,
            'chunks_created': len(chunks)
        })
        
    except Exception as e:
        logger.error(f"Error in upload_and_ingest_document: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/chroma/store_document_embedding', methods=['POST'])
def store_document_embedding():
    """Store document embedding in ChromaDB."""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400
        
        content = data['content']
        metadata = data.get('metadata', {})
        
        rag_manager = get_rag_manager()
        doc_id = rag_manager.store_document_chunk(content, metadata)
        
        return jsonify({
            'success': True,
            'id': doc_id
        })
        
    except Exception as e:
        logger.error(f"Error in store_document_embedding: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/chroma/store_step_embedding', methods=['POST'])
def store_step_embedding():
    """Store step embedding in ChromaDB."""
    try:
        data = request.get_json()
        if not data or 'step_id' not in data:
            return jsonify({'error': 'Step ID is required'}), 400
        
        step_id = data['step_id']
        embedding = data.get('embedding', [])
        metadata = data.get('metadata', {})
        
        # Store step embedding logic here
        # For now, return success
        
        return jsonify({
            'message': 'Step embedding stored successfully',
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in store_step_embedding: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/query', methods=['POST'])
def query_documents():
    """Search documents using vector similarity with optional internet search fallback."""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        top_k = data.get('top_k', 3)
        use_internet_search = data.get('use_internet_search', True)  # Default to True for fallback
        
        rag_manager = get_rag_manager()
        combined_response = rag_manager.query_documents(
            query, 
            n_results=top_k,
            force_internet_search=use_internet_search
        )
        
        return jsonify({
            'success': True,
            'rag_response': combined_response.get('rag_response', {}),
            'internet_search_response': combined_response.get('internet_search_response', None)
        })
        
    except Exception as e:
        logger.error(f"Error in query_documents: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
