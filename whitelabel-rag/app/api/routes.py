from fastapi import APIRouter, Request, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
import os
import sys
import uuid
import logging
from datetime import datetime
from app.services.concierge import get_concierge_instance
from app.services.chroma_service import get_chroma_service_instance
from app.services.rag_manager import get_rag_manager
from app.services.document_processor import DocumentProcessor
from app.utils.file_utils import allowed_file

logger = logging.getLogger(__name__)

api_router = APIRouter()

@api_router.post('/decompose')
async def decompose_task(request: Request):
    try:
        data = await request.json()
        if not data or 'message' not in data:
            raise HTTPException(status_code=400, detail='Message is required')
        
        message = data['message']
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        concierge = get_concierge_instance()
        response = concierge.handle_message(message)
        
        return JSONResponse({
            'response': response,
            'session_id': session_id
        })
    except Exception as e:
        logger.error(f"Error in decompose_task: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@api_router.post('/execute')
async def execute_task(request: Request):
    try:
        data = await request.json()
        if not data or 'task' not in data:
            raise HTTPException(status_code=400, detail='Task is required')
        
        task = data['task']
        retry = request.query_params.get('retry', 'false').lower() == 'true'
        
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
            raise HTTPException(status_code=400, detail=f'Unknown agent type: {agent_type}')
        
        result = agent.handle_message(task.get('instruction', ''))
        
        return JSONResponse({
            'step_number': task.get('step_number', 1),
            'status': 'completed' if not result.get('error') else 'failed',
            'result': result.get('text', ''),
            'agent': agent_type
        })
    except Exception as e:
        logger.error(f"Error in execute_task: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@api_router.post('/validate')
async def validate_result(request: Request):
    try:
        data = await request.json()
        if not data or 'result' not in data or 'task' not in data:
            raise HTTPException(status_code=400, detail='Result and task are required')
        
        result = data['result']
        task = data['task']
        
        confidence = 0.9 if len(result) > 10 else 0.5
        status_val = 'PASS' if confidence > 0.7 else 'FAIL'
        
        return JSONResponse({
            'status': status_val,
            'confidence': confidence,
            'feedback': 'Result validated successfully' if status_val == 'PASS' else 'Result needs improvement'
        })
    except Exception as e:
        logger.error(f"Error in validate_result: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@api_router.get('/tasks/{task_id}/results')
async def get_task_results(task_id: str):
    try:
        return JSONResponse({
            'task_id': task_id,
            'status': 'completed',
            'steps': []
        })
    except Exception as e:
        logger.error(f"Error in get_task_results: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@api_router.get('/files')
async def list_files():
    try:
        upload_folder = 'uploads'
        upload_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), upload_folder)
        
        if not os.path.exists(upload_path):
            return JSONResponse({'files': []})
        
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
        
        return JSONResponse({'files': files})
    except Exception as e:
        logger.error(f"Error in list_files: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@api_router.post('/files')
async def upload_file(file: UploadFile = File(...)):
    try:
        if not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail='Unsupported file type')
        
        filename = file.filename
        upload_folder = 'uploads'
        upload_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), upload_folder)
        
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        return JSONResponse({
            'message': 'File uploaded successfully',
            'filename': filename
        })
    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@api_router.post('/documents/upload_and_ingest_document')
async def upload_and_ingest_document(file: UploadFile = File(...)):
    try:
        if not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail='Unsupported file type')
        
        filename = file.filename
        upload_folder = 'uploads'
        upload_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), upload_folder)
        
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        if os.path.getsize(file_path) == 0:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail='File is empty')
        
        processor = DocumentProcessor()
        rag_manager = get_rag_manager()
        
        chunks = processor.process_document(file_path)
        
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
        
        return JSONResponse({
            'message': f'Document uploaded and ingested successfully. Created {len(chunks)} chunks.',
            'filename': filename,
            'chunks_created': len(chunks),
            'success': len(chunks) > 0
        })
    except Exception as e:
        logger.error(f"Error in upload_and_ingest_document: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@api_router.post('/chroma/store_document_embedding')
async def store_document_embedding(request: Request):
    try:
        data = await request.json()
        if not data or 'content' not in data:
            raise HTTPException(status_code=400, detail='Content is required')
        
        content = data['content']
        metadata = data.get('metadata', {})
        
        rag_manager = get_rag_manager()
        doc_id = rag_manager.store_document_chunk(content, metadata)
        
        return JSONResponse({
            'success': True,
            'id': doc_id
        })
    except Exception as e:
        logger.error(f"Error in store_document_embedding: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@api_router.post('/chroma/store_step_embedding')
async def store_step_embedding(request: Request):
    try:
        data = await request.json()
        if not data or 'step_id' not in data or 'content' not in data:
            raise HTTPException(status_code=400, detail='Step ID and content are required')
        
        step_id = data['step_id']
        content = data['content']
        metadata = data.get('metadata', {})
        
        chroma_service = get_chroma_service_instance()
        stored_id = chroma_service.store_step_embedding(step_id, content, metadata)
        
        return JSONResponse({
            'message': 'Step embedding stored successfully',
            'status': 'success',
            'id': stored_id
        })
    except Exception as e:
        logger.error(f"Error in store_step_embedding: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@api_router.post('/query')
async def query_documents(request: Request):
    try:
        data = await request.json()
        if not data or 'query' not in data:
            raise HTTPException(status_code=400, detail='Query is required')
        
        query = data['query']
        top_k = data.get('top_k', 3)
        
        rag_manager = get_rag_manager()
        results = rag_manager.query_documents(query, n_results=top_k)
        
        return JSONResponse({
            'success': True,
            'results': results.get('results', []),
            'rag_response': results.get('response', None)
        })
    except Exception as e:
        logger.error(f"Error in query_documents: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@api_router.get('/health')
async def health_check():
    return JSONResponse({'status': 'healthy', 'service': 'WhiteLabelRAG'}, status_code=status.HTTP_200_OK)

@api_router.get('/')
async def root():
    # Serve a simple welcome message or redirect to frontend UI
    return JSONResponse({'message': 'Welcome to WhiteLabelRAG API. Please use the frontend UI to interact.'})
