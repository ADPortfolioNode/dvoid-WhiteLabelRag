# WHITE LABEL RAG - IMPLEMENTATION GUIDE
Last updated: June 9, 2025

## PROJECT OVERVIEW

White Label RAG is a scalable Retrieval-Augmented Generation (RAG) application that provides a conversational AI interface with document search capabilities, task decomposition, and guided execution.

### Technology Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| Backend   | Python Flask (port 5000) | REST API server with CORS and modular design |
| Vector DB | ChromaDB (port 8000) | Stores document and step embeddings for semantic search |
| LLM Service | Gemini API (Google) | Powers the conversational AI and task processing |
| Frontend  | React.js + Bootstrap grid layout | Mobile-first, responsive and adaptive UI with real-time updates |
| WebSockets | Flask-SocketIO | Real-time communication between client and server |
| Internet Search | Google Custom Search API | Provides internet search fallback when documents don't have answers |

## RECENT UPDATES (JUNE 2025)

### Internet Search Integration
The application now supports internet search capabilities through Google Custom Search API:

- **Implementation**: Added `InternetSearchAgent` module to handle external web searches
- **Configuration**: Uses `GOOGLE_API_KEY` and `INTERNET_SEARCH_ENGINE_ID` environment variables
- **API Enhancement**: Extended `/api/query` endpoint to support internet search via `use_internet_search` parameter
- **Fallback Logic**: Automatically uses internet search when document search yields no results
- **Testing**: Added comprehensive test scripts in `scripts/test_internet_search.py`

### Documentation Updates
- **[GOOGLE_SEARCH_SETUP.md](GOOGLE_SEARCH_SETUP.md)**: Step-by-step guide for setting up Google Custom Search
- **[INTERNET_SEARCH_CHANGES.md](INTERNET_SEARCH_CHANGES.md)**: Technical summary of all internet search-related changes
- **Environment Templates**: Updated `.env.example` with Google API configuration options
- **Deployment Guides**: Updated Docker and deployment documentation to include new environment variables

## ADDITIONAL RESOURCES

- [README.md](README.md) - Main project documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment instructions
- [GOOGLE_SEARCH_SETUP.md](GOOGLE_SEARCH_SETUP.md) - Google Custom Search setup guide
- [INTERNET_SEARCH_CHANGES.md](INTERNET_SEARCH_CHANGES.md) - Technical details of internet search implementation

## ASSISTANT ARCHITECTURE AND WORKFLOWS

### Assistant Communication Architecture

The WhiteLabelRAG system uses an administrative structure with the Concierge as the consierge dialoging with user and admin assistant is central coordinator. This architectural pattern has been chosen for its balance of flexibility and control.

#### Communication Pattern Options

1. **Chosen Pattern: Hub-and-Spoke with RESTful Communication**
   - Concierge acts as a central hub, coordinating all conversations and tasks
   - Specialized assistants connect to the hub and handle specific tasks
   - Communication happens primarily via REST API calls (not direct object references)
   - Benefits: Clear separation of concerns, easier scaling, better fault isolation

2. **Alternative Pattern: Cloned Multi-Capable Assistants**
   - Each assistant would have full capabilities but specialize in certain tasks
   - Direct object communication within a single process space
   - Benefits: Lower latency, simpler code structure, fewer moving parts
   - Drawbacks: Tighter coupling, more complex code, harder to maintain and scale

3. **Alternative Pattern: Event-Driven Microservices**
   - Each assistant operates as a separate microservice
   - Communication happens via message queue systems (e.g., RabbitMQ, Kafka)
   - Completely decoupled assistants
   - Benefits: Ultimate scalability and resilience
   - Drawbacks: Much higher complexity, more infrastructure requirements

### Concierge Agent Workflows

#### Hierarchical Workflow Architecture

The WhiteLabelRAG system implements a hierarchical workflow pattern for handling user interactions, with the Concierge acting as the main dialogue interface and orchestrator.

1. **Conversation Context Management**
   - The Concierge maintains a conversation history for each unique user session
   - Conversation context is stored in a session store (Redis or in-memory store)
   - Maximum conversation window: Last 8-10 exchanges by default (configurable)
   - The context includes:
     ```json
     {
       "session_id": "unique-session-id",
       "messages": [
         {
           "role": "user",
           "content": "What documents do you have about climate change?",
           "timestamp": "2023-04-15T14:32:10Z"
         },
         {
           "role": "assistant",
           "content": "I have several documents on climate change...",
           "timestamp": "2023-04-15T14:32:15Z",
           "sources": ["climate_report_2023.pdf", "ipcc_analysis.txt"]
         }
       ],
       "user_info": {},
       "conversation_state": "information_gathering",
       "last_activity": "2023-04-15T14:32:15Z"
     }
     ```

2. **Conversation Classification**
   - Concierge classifies each user message into different intent categories:
     - **Simple Query**: Direct question answerable from context
     - **Document Search**: Request to find information in documents
     - **Task Request**: Multi-step task requiring decomposition
     - **Clarification**: User asking for clarification or followup
     - **Feedback**: User providing feedback on previous response
     - **Meta**: Question about the system itself
   - Classification uses a prompt-based approach with the LLM

3. **Hierarchical Workflow Process**
   - **Layer 1 - Concierge**: Main dialogue interface with users
     - Handles simple queries directly
     - Routes document search requests to SearchAgent
     - For complex tasks, delegates to Task Assistant
   
   - **Layer 2 - Task Assistant**: For complex, multi-step tasks
     - Breaks down tasks into logical steps
     - Creates a plan for task execution
     - Instantiates and manages specialized Step Assistants
     - Validates results before returning to Concierge
   
   - **Layer 3 - Step Assistants**: Specialized clones for each step
     - **SearchAgent**: Specialized for document retrieval
     - **FileAgent**: Specialized for file operations
     - **FunctionAgent**: Specialized for function execution
     - Each Step Assistant has a focused scope and specialized knowledge
   
   - **Response Assembly**:
     - Main content from validated Step Assistant results
     - Source attribution (if using RAG)
     - Follow-up suggestions (optional)
     - Confidence indicators (optional)

4. **Fallback Mechanism**
   - If the hierarchical workflow fails, system falls back to direct execution
   - Direct execution uses the hub-and-spoke pattern for simpler tasks

> **Note**: For a visual representation of the hierarchical workflow architecture, refer to the mermaid diagram in `hierarchical_workflow_diagram.md`. For details about the TaskAssistant implementation, see `task_assistant.md`.

#### Industry Standard RAG Workflows

> **Note**: The following industry standard RAG workflows work within our hierarchical workflow architecture. The Task Assistant selects and implements the appropriate RAG workflow based on the task requirements.

1. **Single-Stage RAG (Basic)**
   - **Workflow**: Query → Retrieve → Generate
   - **Process**:
     - User query is processed directly
     - Documents retrieved based on vector similarity
     - Response generated with retrieved context
   - **Implementation**:
     ```python
     def basic_rag_workflow(query, top_k=3):
         # Retrieve relevant documents
         retrieved_docs = chroma_service.query(query, top_k=top_k)
         
         # Format context from retrieved documents
         context = "\n".join([doc.content for doc in retrieved_docs])
         
         # Generate response using LLM with context
         response = llm.generate_response(
             query=query, 
             context=context,
             sources=[doc.metadata.get('source') for doc in retrieved_docs]
         )
         
         return response
     ```
   - **Use Cases**: Simple factual queries, straightforward information retrieval

2. **Multi-Stage RAG (Advanced)**
   - **Workflow**: Query → Query Processing → Retrieval → Filtering → Generation → Post-processing
   - **Process**:
     - User query is analyzed and expanded for better recall
     - Multiple retrieval strategies used in parallel (semantic, keyword, etc.)
     - Retrieved documents filtered and reranked for relevance
     - Response generated with carefully selected context
     - Post-processing adds metadata, citations, confidence scores
   - **Implementation**:
     ```python
     def advanced_rag_workflow(query):
         # Query processing
         expanded_query = query_expander.expand(query)
         
         # Multi-strategy retrieval
         semantic_results = vector_store.query(expanded_query, top_k=5)
         keyword_results = keyword_store.search(expanded_query, top_k=5)
         
         # Merge and rerank results
         merged_results = merge_search_results(semantic_results, keyword_results)
         reranked_results = reranker.rerank(merged_results, query)
         
         # Format context from top results
         context = format_context(reranked_results[:3])
         
         # Generate response
         response = llm.generate_response(query, context)
         
         # Post-process with citations
         response_with_citations = citation_processor.add_citations(
             response, reranked_results
         )
         
         return response_with_citations
     ```
   - **Use Cases**: Complex queries, high-stakes information needs, specialized domains

3. **Recursive RAG**
   - **Workflow**: Query → Initial Retrieval → Response Planning → Targeted Retrieval → Generation
   - **Process**:
     - Initial retrieval provides a broad context
     - Response is planned based on initial context
     - Targeted retrievals performed for each part of the response plan
     - Final response generated with comprehensive context
   - **Implementation**:
     ```python
     def recursive_rag_workflow(query):
         # Initial retrieval for planning
         initial_docs = retriever.get_documents(query, top_k=3)
         
         # Plan response components
         response_plan = llm.plan_response(query, format_context(initial_docs))
         
         # Targeted retrieval for each component
         component_contexts = {}
         for component in response_plan['components']:
             sub_query = component['search_query']
             component_docs = retriever.get_documents(sub_query, top_k=2)
             component_contexts[component['id']] = format_context(component_docs)
         
         # Generate comprehensive response
         final_response = llm.generate_structured_response(
             query, 
             response_plan, 
             component_contexts
         )
         
         return final_response
     ```
   - **Use Cases**: Multi-part questions, complex analyses, detailed explanations

4. **Adaptive RAG**
   - **Workflow**: Query → Analysis → Strategy Selection → Execution → Evaluation → Refinement
   - **Process**:
     - Query analyzed to determine optimal retrieval strategy
     - Appropriate RAG workflow selected dynamically
     - Initial response generated and evaluated for quality
     - Response refined if necessary to improve accuracy
   - **Implementation**:
     ```python
     def adaptive_rag_workflow(query):
         # Analyze query complexity and type
         query_analysis = query_analyzer.analyze(query)
         
         # Select appropriate workflow
         if query_analysis.is_simple_factual():
             initial_response = basic_rag_workflow(query)
         elif query_analysis.is_multi_part():
             initial_response = recursive_rag_workflow(query)
         else:
             initial_response = advanced_rag_workflow(query)
         
         # Evaluate response quality
         quality_score = response_evaluator.evaluate(
             query, initial_response
         )
         
         # Refine if needed
         if quality_score < 0.8:
             refined_response = response_refiner.refine(
                 query, initial_response
             )
             return refined_response
         
         return initial_response
     ```
   - **Use Cases**: Production systems serving diverse query types, mission-critical applications

#### Inter-Assistant Communication

1. **API-Based Communication Flow**
   - Concierge-to-Specialist communication happens via HTTP API calls
   - Example workflow:
     ```
     User → Frontend → API → Concierge → [API] → SearchAgent → [API] → Concierge → API → Frontend → User
     ```
   - Each arrow represents an API call or message passing boundary

2. **Communication Protocol**
   - All inter-assistant communication uses standardized JSON messages
   - Base message format:
     ```json
     {
       "message_id": "uuid-string",
       "from_assistant": "Concierge",
       "to_assistant": "SearchAgent",
       "request_type": "document_search",
       "content": {
         "query": "Find information about climate change impacts",
         "parameters": {
           "top_k": 3,
           "min_relevance": 0.7
         }
       },
       "context": {
         "session_id": "user-session-uuid", 
         "conversation_id": "conversation-uuid",
         "task_id": "task-uuid-if-part-of-task"
       },
       "timestamp": "2023-04-15T14:32:10Z"
     }
     ```
   - Responses follow a similar format with additional `"result"` field

3. **Coordination Mechanisms**
   - **Task Queue**: For asynchronous processing
   - **Status Updates**: Real-time WebSocket updates during processing
   - **Error Handling**: Standardized error responses and retry mechanisms
   - **Timeout Handling**: Deadlines for requests to prevent hanging tasks

### Specialized Assistant Integration

#### SearchAgent Integration

1. **Activation**
   - Triggered by Concierge via POST to `/api/execute` with `"suggested_agent_type": "SearchAgent"`
   - Input: Search query, optional filters, and parameters
   - Output: Formatted search results with metadata and sources

2. **Core Functions**
   - Search document repository
   - Rerank results for relevance
   - Format response with source attribution

#### FileAgent Integration

1. **Activation**
   - Triggered by Concierge via POST to `/api/execute` with `"suggested_agent_type": "FileAgent"`
   - Input: File operation details and parameters
   - Output: Operation results and status

2. **Core Functions**
   - Process document uploads
   - List available documents
   - Extract metadata from documents

#### FunctionAgent Integration

1. **Activation**
   - Triggered by Concierge via POST to `/api/execute` with `"suggested_agent_type": "FunctionAgent"`
   - Input: Function name, parameters, and constraints
   - Output: Function execution results

2. **Core Functions**
   - Execute specific predefined functions
   - Transform data formats
   - Integrate with external APIs

### Implementation Decisions and Recommendations

#### Architecture Recommendation: RESTful API-based Communication

The WhiteLabelRAG system uses RESTful API-based communication between assistants rather than direct object references or shared memory for several key reasons:

1. **Decoupling and Flexibility**
   - Each assistant can be developed, tested, and deployed independently
   - Assistants can be written in different languages or frameworks if needed
   - API contracts ensure clear interfaces between components

2. **Scalability**
   - Assistants can be deployed on separate servers or containers
   - Horizontal scaling of individual assistants based on load
   - Independent resource allocation based on assistant needs

3. **Resilience**
   - Failure in one assistant doesn't crash the entire system
   - Retry mechanisms can be implemented at API boundaries
   - Easier monitoring and debugging of inter-assistant communication

4. **Security**
   - Clear boundaries for permission and access control
   - Ability to implement authentication between assistant APIs
   - Better isolation of sensitive operations

5. **Evolution Path**
   - Easier migration to microservices if needed
   - Assistants can be replaced with new implementations without affecting others
   - Versioning of assistant APIs for backward compatibility

For systems with lower complexity requirements or tighter performance constraints, the cloned assistant approach with direct object communication might be preferable. However, for enterprise-grade applications with evolving requirements, the RESTful API approach offers better long-term maintenance and scaling properties.

## RAG WORKFLOW ARCHITECTURE

### 1. User Interaction Flow
- User submits query through the web interface
- Real-time status updates provided via WebSockets
- Query is processed by the Concierge Agent if it's a task, if not continue pleasant conversation.
- Response with sources is displayed to the user

### 2. Query Processing Pipeline
1. **Task Reception & Decomposition**
   - Concierge Agent receives user conversation or query via `POST /api/decompose`
   - LLM decomposes task into structured JSON list of steps or maintains conversation
   - Each step includes agent type assignment for specialized processing

2. **Task Execution**
   - Steps executed through specialized agents via `POST /api/execute`
   - Different agent types (SearchAgent, FileAgent, FunctionAgent) handle specialized tasks
   - For retrieval tasks, multiple document sources are consulted

3. **Validation & Feedback**
   - `POST /api/validate` compares step results against original criteria
   - Failed steps (≤3 retries): feedback loop to `/api/execute?retry=true` 
   - Passed steps: persist vector via `/api/chroma/store_step_embedding`

4. **Result Aggregation**
   - Once all steps validated, Concierge Agent compiles final output
   - UI receives updates via WebSockets or by polling `GET /api/tasks/{id}/results`
   - Sources are attributed in the final response

## API REFERENCE

### Core Task Processing Endpoints

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/api/decompose` | POST | Decompose user task into steps | `{ "message": "string" }` | `{ "response": { "text": "string", "media": "string?", "sources": ["string"] } }` |
| `/api/execute` | POST | Execute decomposed task step | `{ "task": { "step_number": int, "instruction": "string", "suggested_agent_type": "string" } }` | `{ "step_number": int, "status": "string", "result": "string" }` |
| `/api/validate` | POST | Validate step result | `{ "result": "string", "task": { "step_number": int, "instruction": "string" } }` | `{ "status": "PASS" \| "FAIL", "confidence": float, "feedback": "string" }` |
| `/api/tasks/{task_id}/results` | GET | Get task results | N/A | `{ "task_id": "string", "status": "string", "steps": [] }` |

### Document Management Endpoints

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/api/files` | GET | List uploaded documents | N/A | `{ "files": [{ "id": "string", "name": "string" }] }` |
| `/api/files` | POST | Upload document | `multipart/form-data with 'file'` | `{ "message": "string", "filename": "string" }` |
| `/api/documents/upload_and_ingest_document` | POST | Upload and ingest | `multipart/form-data with 'file'` | `{ "message": "string", "filename": "string" }` |

### ChromaDB Integration Endpoints

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/api/chroma/store_document_embedding` | POST | Store document embedding | `{ "content": "string", "metadata": {} }` | `{ "success": boolean, "id": "string?" }` |
| `/api/chroma/store_step_embedding` | POST | Store step embedding | `{ "step_id": "string", "embedding": [], "metadata": {} }` | `{ "message": "string", "status": "string" }` |
| `/api/query` | POST | Search passages | `{ "query": "string", "top_k": int }` | `{ "success": boolean, "results": [] }` |

### WebSocket Events

| Event | Direction | Description | Data Structure |
|-------|-----------|-------------|----------------|
| `connect` | Client → Server | Establish connection | N/A |
| `disconnect` | Client → Server | End connection | N/A |
| `chat_response` | Server → Client | Assistant responses | `{ "text": "string", "sources": [] }` |
| `assistant_status` | Server → Client | Status updates | `{ "status": "string", "progress": int, "details": "string" }` |

## ASSISTANT CONFIGURATION AND IMPLEMENTATION DETAILS

### Assistant Types and Configurations

#### Concierge Agent
- **Role**: Main orchestrator and entry point for all user interactions
- **Capabilities**:
  - Task decomposition into optimal steps
  - Routing to specialized agents
  - Response aggregation and formatting
  - Conversation memory and context management
- **Configuration**:
  ```json
  {
    "name": "Concierge",
    "model": "gemini-pro",
    "temperature": 0.2,
    "max_tokens": 1024,
    "system_prompt": "You are the WhiteLabelRAG Concierge, an expert assistant that helps users find information and complete tasks."
  }
  ```
- **Class Implementation**:
  ```python
  class Concierge(BaseAssistant):
      def __init__(self):
          super().__init__("Concierge")
          self.chroma_service = get_chroma_service_instance()
          self.rag_manager = get_rag_manager()
          self.llm = LLMFactory.get_llm()
          self.direct_functions = AVAILABLE_FUNCTIONS
          # Initialize conversation store
          self.conversation_store = ConversationStore()
          
      def handle_message(self, message: str):
          # Get or create conversation context
          session_id = get_current_session_id()
          conversation = self.conversation_store.get_conversation(session_id)
          
          # Add user message to conversation
          conversation.add_message("user", message)
          
          # Classify the message intent
          intent = self._classify_intent(message, conversation)
          
          # Process based on intent
          if intent == "document_search":
              return self._handle_document_search(message, conversation)
          elif intent == "task_request":
              return self._handle_task_decomposition(message, conversation)
          else:
              return self._generate_direct_response(message, conversation)
  ```

#### SearchAgent
- **Role**: Specialized for document retrieval and RAG operations
- **Capabilities**:
  - Query expansion for better recall
  - Multi-document retrieval
  - Result ranking and filtering
  - Source attribution
- **Configuration**:
  ```json
  {
    "name": "SearchAgent",
    "model": "gemini-pro",
    "temperature": 0.1,
    "max_tokens": 1024,
    "system_prompt": "You are a search specialist that retrieves relevant document information from the knowledge base."
  }
  ```
- **Class Implementation**:
  ```python
  class SearchAgent(BaseAssistant):
      def __init__(self):
          super().__init__("SearchAgent")
          self.chroma_service = get_chroma_service_instance()
          self.rag_manager = get_rag_manager()
          self.llm = LLMFactory.get_llm()
          
      def handle_message(self, message):
          # Process search query
          self._update_status("running", 10, "Processing search query...")
          
          # Get collection stats
          collection_stats = self.rag_manager.get_collection_stats()
          
          # Execute search
          results = self.rag_manager.query_documents(message, n_results=5)
          
          # Format results
          formatted_results = self._format_advanced_results(results.get("results", []))
          
          # Return response
          return self.report_success(text=formatted_results)
  ```

#### FileAgent
- **Role**: Handles file operations and document management
- **Capabilities**:
  - Document upload processing
  - Format conversion
  - Metadata extraction
  - Content chunking
- **Configuration**:
  ```json
  {
    "name": "FileAgent",
    "model": "gemini-pro",
    "temperature": 0.1,
    "max_tokens": 512,
    "system_prompt": "You are a file processing specialist that handles document uploads and information extraction."
  }
  ```
- **Class Implementation**:
  ```python
  class FileAgent(BaseAssistant):
      def __init__(self):
          super().__init__("FileAgent")
          self.uploads_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))
          
      def handle_message(self, message):
          # Check if it's a file listing request
          if "list" in message.lower() and "file" in message.lower():
              return self._list_files()
              
          # Check for file processing requests
          file_path = self._extract_file_path(message)
          if file_path:
              return self._process_file(file_path, message)
              
          # Default response
          return self.report_failure("I'm not sure what file operation you want me to perform.")
  ```

#### FunctionAgent
- **Role**: Executes specialized functions and API integrations
- **Capabilities**:
  - API calling
  - Function execution
  - Data transformation
  - External service integration
- **Configuration**:
  ```json
  {
    "name": "FunctionAgent",
    "model": "gemini-pro",
    "temperature": 0.1,
    "max_tokens": 512,
    "system_prompt": "You are a function execution specialist that runs operations safely based on user needs."
  }
  ```
- **Class Implementation**:
  ```python
  class FunctionAgent(BaseAssistant):
      def __init__(self):
          super().__init__("FunctionAgent")
          self.llm = LLMFactory.get_llm()
          self.available_functions = AVAILABLE_FUNCTIONS
          
      def handle_message(self, message):
          # Analyze request
          function_call = self._extract_function_call(message)
          
          if function_call and function_call["name"] in self.available_functions:
              # Execute function
              result = self._execute_function(function_call)
              return self.report_success(text=result)
          else:
              return self.report_failure("No valid function call could be extracted from the request.")
  ```

### Base Assistant Implementation

All assistant types inherit from a common `BaseAssistant` class that provides:

```python
class BaseAssistant:
    def __init__(self, name):
        self.name = name
        self.status = "idle"
        self.progress = 0
        self.details = "Initialized"
        
    def _update_status(self, status, progress, details):
        self.status = status
        self.progress = progress
        self.details = details
        
        # Emit WebSocket event with status update
        socketio.emit('assistant_status_update', {
            'assistant_id': id(self),
            'name': self.name,
            'status': status,
            'progress': progress,
            'details': details
        })
        
    def report_success(self, text, additional_data=None):
        self._update_status("completed", 100, "Task completed successfully")
        result = {
            "text": text,
            "assistant": self.name,
            "timestamp": datetime.now().isoformat()
        }
        
        if additional_data:
            result.update(additional_data)
            
        return result
        
    def report_failure(self, error_message):
        self._update_status("failed", 100, error_message)
        return {
            "text": error_message,
            "assistant": self.name,
            "timestamp": datetime.now().isoformat(),
            "error": True
        }
```

### RAG Document Processing Workflow

1. **Document Upload**
   - User uploads document to `/api/files` or `/api/documents/upload_and_ingest_document` endpoint
   - File is stored in `uploads/` directory
   - FileAgent validates document format (PDF, TXT, DOCX, etc.)

2. **Document Processing**
   - Text extraction from document
   - Content chunking (configurable size: 500 tokens default with 50 token overlap)
   - Metadata extraction (filename, timestamp, source, etc.)

3. **Vector Embedding**
   - Chunks are processed through embedding model (Google Generative AI embedding function)
   - Embeddings stored in ChromaDB with their metadata
   - Document ID mapping maintained for retrieval

4. **Retrieval Process**
   - User query embedded using same embedding model
   - Vector similarity search executed against ChromaDB
   - Top-k results (configurable, default: 3) retrieved based on similarity
   - Optional re-ranking using Cross-Encoder or LLM-based relevance scoring

5. **Response Generation**
   - Retrieved documents assembled into context window
   - LLM generates response using retrieved context
   - Source attribution appended to response

## USER INTERFACE IMPLEMENTATION

### Chat Interface Design

The WhiteLabelRAG chat interface uses a modern, responsive design that follows best UI/UX practices for conversational interfaces:

1. **Message Layout**: Messages are displayed as floating "bubbles" aligned to either side of the chat container.
   - User messages: Right-aligned with blue background
   - Assistant messages: Left-aligned with light gray background and border
   - Each message shows clear visual distinction between user and assistant

2. **Status Indicator**: A prominent status badge at the top of the chat interface provides real-time feedback:
   - Visual indicator (green dot with pulse animation for active processing)
   - Text status message showing current assistant state
   - Progress bar for long-running operations
   - Status updates via WebSocket in real-time

3. **CSS Implementation**:
   ```css
   .chat-container {
       min-height: 300px;
       max-height: 500px;
       overflow-y: auto;
       padding: 1rem;
       border-radius: 0.5rem;
       border: 1px solid #dee2e6;
       margin-bottom: 1rem;
       background: #fff;
   }
   
   .message {
       max-width: 85%;
       margin-bottom: 1rem;
       clear: both;
       word-wrap: break-word;
   }
   
   .message-user {
       float: right;
       text-align: right;
       background: #007bff;
       color: white;
       border-radius: 1rem 1rem 0 1rem;
       padding: 0.75rem 1rem;
   }
   
   .message-assistant {
       float: left;
       text-align: left;
       background: #f8f9fa;
       border: 1px solid #dee2e6;
       border-radius: 1rem 1rem 1rem 0;
       padding: 0.75rem 1rem;
   }
   
   .status-badge {
       display: inline-flex;
       align-items: center;
       padding: 0.5rem 1rem;
       border-radius: 2rem;
       background: #f8f9fa;
       border: 1px solid #dee2e6;
       margin-bottom: 1rem;
   }
   ```

4. **Message Addition JavaScript**:
   ```javascript
   function addMessage(content, isUser = false) {
       const messageDiv = document.createElement('div');
       messageDiv.className = `message message-${isUser ? 'user' : 'assistant'}`;
       messageDiv.textContent = content;
       chatBox.appendChild(messageDiv);
       chatBox.scrollTop = chatBox.scrollHeight;
   }
   ```

5. **Status Update Mechanism**:
   ```javascript
   function updateStatus(status, progress = null) {
       statusText.textContent = status;
       if (progress !== null) {
           progressBar.style.width = `${progress}%`;
       }
       
       // Update indicator state
       statusIndicator.classList.toggle('active', status.toLowerCase().includes('processing'));
   }
   ```

### WebSocket Implementation

The WhiteLabelRAG application uses Socket.IO for real-time bidirectional communication with enhanced reliability:

1. **Connection Configuration**:
   ```javascript
   const socketOptions = {
     transports: ['websocket', 'polling'],  // Try WebSocket first, fallback to polling
     reconnection: true,
     reconnectionAttempts: 15,
     reconnectionDelay: 1000,
     reconnectionDelayMax: 8000,
     timeout: 30000,
     autoConnect: true,
     forceNew: false,
     upgrade: true,
     rememberUpgrade: true,
     pingInterval: 15000,  // Health check every 15 seconds
     pingTimeout: 10000    // Wait 10 seconds for pong response
   };
   ```

2. **Health Check System**:
   - Client sends regular health check pings
   - Server monitors connection health
   - Automatic reconnection with exponential backoff
   - Client-side connection state tracking

3. **Event Handling**:
   - `connect`: Successfully connected to server
   - `disconnect`: Connection lost (with reason)
   - `connect_error`: Error during connection attempt
   - `assistant_status_update`: Status updates from assistant
   - `chat_message`: Incoming message from assistant
   - `health_check`: Connection health verification
   
4. **Error Recovery**:
   - Automatically attempts reconnection on connection loss
   - Graceful degradation when WebSocket is unavailable
   - Clear user feedback during connection issues
   - Session persistence across reconnections

### RAG Document Processing Flow

The document processing in WhiteLabelRAG follows this workflow:

1. **Upload Phase**:
   - User uploads document via web interface
   - Document stored in `uploads/` directory
   - File validation performed (format, size, security)

2. **Processing Phase**:
   ```
   Document → Text Extraction → Chunking → Embedding → Storage in ChromaDB
   ```

3. **Extraction Methods**:
   - PDF: PyPDFLoader
   - DOCX: docx library
   - TXT: direct text loading
   - MD: markdown → html → plain text
   - CSV/Excel: structured data handling

4. **Vector Storage**:
   - Uses ChromaDB as vector database
   - Implements resilience patterns:
     - Circuit breaker for database protection
     - Automatic retries with exponential backoff
     - Connection pooling
     - Error isolation

5. **Query Processing**:
   - Query converted to embedding vector
   - Similarity search in ChromaDB
   - Results ranked by relevance 
   - Top-k passages returned with metadata
   - LLM synthesizes final response with citations

## TESTING AND TROUBLESHOOTING

### Unit and Integration Testing

1. **Test Frameworks**:
   - `pytest` for unit testing Python code
   - `pytest-flask` for testing Flask applications
   - `pytest-socketio` for testing Socket.IO events
   - `factory_boy` for test data generation

2. **Test Organization**:
   - Unit tests: `tests/unit/`
   - Integration tests: `tests/integration/`
   - End-to-end tests: `tests/e2e/`
   - Fixtures and factories: `tests/factories.py`, `tests/fixtures.py`

3. **Sample Tests**:
   ```python
   # tests/unit/test_concierge.py
   def test_handle_message_simple_query():
       concierge = Concierge()
       response = concierge.handle_message("What's the capital of France?")
       assert response['text'] == "The capital of France is Paris."
   
   # tests/integration/test_api.py
   def test_decompose_task():
       response = client.post('/api/decompose', json={
           "message": "Book a flight from NYC to London"
       })
       assert response.status_code == 200
       assert "steps" in response.json['task']
   ```

### Common Issues and Solutions

1. **Issue: Assistant not responding**:
   - Check WebSocket connection in browser console
   - Ensure server is running and accessible
   - Look for errors in server logs

2. **Issue: Invalid API response format**:
   - Use API documentation to verify request/response structure
   - Check for middleware or transformation errors

3. **Issue: File upload failing**:
   - Verify file size and type against server limits
   - Check storage permissions and available space

4. **Issue: Vector search not returning results**:
   - Ensure documents are properly indexed in ChromaDB
   - Check query syntax and parameters

5. **Issue: Assistant status not updating**:
   - Verify WebSocket event handling in frontend
   - Check for JavaScript errors in browser console

### Performance Optimization Tips

1. **Backend Optimizations**:
   - Use connection pooling for database and Redis connections
   - Optimize ChromaDB queries with proper indexing
   - Profile and optimize Python code with cProfile or Py-Spy

2. **Frontend Optimizations**:
   - Minimize bundle size with code splitting and lazy loading
   - Optimize images and static assets
   - Use memoization and React's `useMemo`/`useCallback` hooks

3. **Database Optimizations**:
   - Regularly vacuum and analyze PostgreSQL database
   - Optimize ChromaDB configuration for caching and memory usage

4. **Caching Strategies**:
   - Use Redis or Memcached for caching frequent queries and results
   - Implement HTTP caching headers for static assets

5. **Load Testing**:
   - Use `locust` or `JMeter` to simulate load and identify bottlenecks
   - Monitor resource usage and response times under load

6. **Monitoring and Alerting**:
   - Use Prometheus and Grafana for monitoring application metrics
   - Set up alerts for error rates, latency, and resource usage spikes

## SECURITY CONSIDERATIONS

### Authentication and Authorization

1. **API Key Security**:
   - Use strong, unique API keys for each service
   - Rotate API keys regularly and revoke unused keys
   - Store API keys in environment variables or secure vaults

2. **User Authentication**:
   - Implement OAuth 2.0 or OpenID Connect for user authentication
   - Support single sign-on (SSO) with enterprise identity providers
   - Use secure cookies or tokens for session management

3. **Role-Based Access Control (RBAC)**:
   - Define roles and permissions for each user type
   - Restrict access to sensitive endpoints and operations
   - Implement attribute-based access control (ABAC) if needed

4. **Audit Logging**:
   - Log all authentication attempts, both successful and failed
   - Log access to sensitive data and configuration changes
   - Use a centralized logging solution for monitoring and alerting

### Data Security

1. **Data Encryption**:
   - Use TLS/SSL for encrypting data in transit
   - Encrypt sensitive data at rest using strong encryption algorithms
   - Use environment-specific keys for encryption and decryption

2. **Sensitive Data Handling**:
   - Mask or redact sensitive data in logs and error messages
   - Limit sensitive data exposure through API responses

3. **Backup and Recovery**:
   - Regularly back up databases and critical data
   - Test backup and recovery procedures periodically

4. **Vulnerability Management**:
   - Regularly update dependencies and apply security patches
   - Use static and dynamic analysis tools for vulnerability scanning
   - Conduct regular security audits and penetration testing

5. **Network Security**:
   - Use firewalls and security groups to restrict network access
   - Isolate sensitive services and databases in private subnets
   - Use VPN or dedicated connections for secure access

6. **Container Security**:
   - Use official and minimal base images for containers
   - Regularly scan container images for vulnerabilities
   - Use read-only file systems and restrict container capabilities

## DEPLOYMENT GUIDE

### System Requirements

- **Backend Server**: 
  - Python 3.9+ with Flask
  - 4+ CPU cores recommended
  - 8GB+ RAM recommended (4GB minimum)
  - 10GB+ storage for document storage and vector database

- **Vector Database**:
  - ChromaDB instance (embedded or separate service)
  - If separate: 4GB+ RAM recommended
  - SSD storage recommended for performance

- **LLM Provider**:
  - API key for Gemini API
  - Internet connection for API access
  - Rate limit considerations for production deployment

### Deployment Options

#### Docker Deployment (Recommended)

1. **Build the Docker image**:
   ```shell
   docker build -t whitelabel-rag:latest .
   ```

2. **Run with embedded ChromaDB**:
   ```shell
   docker run -p 5000:5000 -e GEMINI_API_KEY=your_api_key whitelabel-rag:latest
   ```

3. **Run with external ChromaDB**:
   ```shell
   docker-compose up -d
   ```

4. **Configuration**:
   - Environment variables can be set in `.env` file or during `docker run`
   - Mount volumes for persistent data:
     ```shell
     docker run -v ./uploads:/app/uploads -v ./chromadb_data:/app/chromadb_data -p 5000:5000 whitelabel-rag:latest
     ```

#### Manual Deployment

1. **Set up Python environment**:
   ```shell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```shell
   # Create .env file with:
   GEMINI_API_KEY=your_api_key
   FLASK_ENV=production
   CHROMA_DB_IMPL=duckdb+parquet
   CHROMA_DB_PATH=./chromadb_data
   ```

3. **Run the application**:
   ```shell
   python run.py
   ```

### Production Considerations

1. **Security**:
   - Set `SECRET_KEY` environment variable to a strong random value
   - Enable HTTPS with proper SSL certificates
   - Implement authentication for API endpoints
   - Consider using a reverse proxy (e.g., Nginx, Traefik)

2. **Scaling**:
   - Horizontal scaling:
     - Use load balancer for multiple Flask instances
     - Ensure shared ChromaDB access or consistent routing
   - Vertical scaling:
     - Increase RAM for larger document sets
     - Add CPU cores for concurrent user handling

3. **Monitoring**:
   - Implement application logging
   - Monitor system resources (CPU, memory, disk)
   - Set up alerts for service disruptions
   - Track ChromaDB performance metrics

4. **Backup Strategy**:
   - Regular backups of `uploads/` directory
   - Regular backups of `chromadb_data/` directory
   - Document metadata database backups
   - Configuration backups

### Troubleshooting Common Issues

1. **Vector Database Connection Failures**:
   - Check ChromaDB service status
   - Verify network connectivity
   - Check persistence path permissions
   - Review circuit breaker logs

2. **Document Processing Errors**:
   - Validate file formats are supported
   - Check for file corruption
   - Monitor memory usage during large file processing
   - Review extraction logs

3. **Performance Issues**:
   - Monitor query latency
   - Check vector database index size
   - Review connection pooling configuration
   - Adjust chunk size for optimal performance

4. **API Rate Limit Errors**:
   - Implement request throttling
   - Cache common responses
   - Use batch processing where applicable
   - Monitor API usage metrics

## MAINTENANCE AND UPDATES

### Regular Maintenance Tasks

1. **Backup Procedures**:
   - Schedule regular backups of databases and critical data
   - Test backup and recovery procedures periodically

2. **Software Updates**:
   - Regularly update application dependencies and server software
   - Apply security patches and updates in a timely manner

3. **Performance Monitoring**:
   - Monitor application performance and resource usage
   - Optimize queries, indexes, and application code as needed

4. **Log Management**:
   - Rotate and archive logs regularly
   - Monitor logs for errors, warnings, and suspicious activity

5. **Security Audits**:
   - Conduct regular security audits and vulnerability assessments
   - Remediate identified vulnerabilities and risks

6. **Documentation Updates**:
   - Keep system documentation, API docs, and user guides up to date
   - Document any changes or updates to the system

### Support Procedures

1. **Issue Tracking**:
   - Use an issue tracker (e.g., Jira, GitHub Issues) to manage and prioritize issues
   - Assign issues to appropriate team members for resolution

2. **Incident Response**:
   - Define and document incident response procedures
   - Assign roles and responsibilities for incident response

3. **User Support**:
   - Provide support channels (e.g., email, chat, ticketing system) for users to report issues or ask questions
   - Define response and resolution time targets for user support requests

4. **Maintenance Windows**:
   - Schedule regular maintenance windows for updates, backups, and other maintenance tasks
   - Notify users in advance of any planned downtime or service interruptions

5. **Service Level Agreements (SLAs)**:
   - Define SLAs for system availability, performance, and support response times
   - Monitor and report on SLA compliance

6. **Continuous Improvement**:
   - Regularly review and analyze system performance, support metrics, and user feedback
   - Identify and implement opportunities for improvement

# WhiteLabelRAG Instructions

## Overview
This document provides configuration guidelines for the WhiteLabelRAG system. The system uses a Retrieval-Augmented Generation (RAG) approach to answer questions based on your documents.

## Configuration Parameters

### Embedding Models
The following embedding models are supported:
- `all-MiniLM-L6-v2` (Default, fastest)
- `text-embedding-ada-002` (OpenAI, requires API key)
- `sentence-t5-base` (Good balance of performance and accuracy)

### Document Types
The system supports the following document types:
- PDF (`.pdf`)
- Text (`.txt`)
- Word Documents (`.docx`)
- Markdown (`.md`)

## Starting the Application

### Using Docker
To start the application using Docker, run the following script from the `whitelabel-rag/scripts` directory:

```bat
run-docker.bat
```

This script will build and start the application, Redis, and optionally the Nginx reverse proxy using Docker Compose.

### Local Development
For local development, you can use the following scripts from the `whitelabel-rag/scripts` directory:

- `run-local.bat`: Starts the application locally in development mode by setting necessary environment variables and running `python run.py`.
- `run-dev.bat`: Starts the development environment with virtual environment activation, environment variable checks, and debug mode enabled.

Make sure to set the required environment variables such as `GEMINI_API_KEY` before running these scripts.

## Integration Guidelines
When integrating with your application:
1. Initialize the RAG system with your document repository
2. Adjust the top-k parameter based on your requirements (3-5 is recommended)
3. Process queries through the provided API

## Performance Considerations
- Large document collections require more memory
- Initial indexing may take time for large collections
- Consider chunking strategies for very large documents

## Customization
The system can be customized by modifying the following components:
- Document Loader: For custom document types
- Retriever: For different search algorithms
- Generator: For custom response generation logic
