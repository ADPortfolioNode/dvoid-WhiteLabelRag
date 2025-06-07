"""
API routes for WhiteLabelRAG
"""

import os
import uuid
import logging
from datetime import datetime
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from . import api_bp
from app.services.concierge import get_concierge_instance
from app.services.chroma_service import get_chroma_service_instance
from app.services.rag_manager import get_rag_manager
from app.services.document_processor import DocumentProcessor
from app.services.internet_search_agent import get_internet_search_agent_instance
from app.services.multimedia_agent import get_multimedia_agent_instance
from app.utils.file_utils import allowed_file


logger = logging.getLogger(__name__)

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
    """Search documents using vector similarity."""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        top_k = data.get('top_k', 3)
        use_internet_search = data.get('use_internet_search', False)
        
        if use_internet_search:
            internet_search_agent = get_internet_search_agent_instance()
            result = internet_search_agent.search(query, num_results=top_k)
            return jsonify({
                'success': not result.get('error'),
                'results': result.get('additional_data', {}).get('results', []),
                'text': result.get('text', ''),
                'agent': 'InternetSearchAgent'
            })
        else:
            rag_manager = get_rag_manager()
            results = rag_manager.query_documents(query, n_results=top_k)
            return jsonify({
                'success': True,
                'results': results.get('results', [])
            })
        
    except Exception as e:
        logger.error(f"Error in query_documents: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
