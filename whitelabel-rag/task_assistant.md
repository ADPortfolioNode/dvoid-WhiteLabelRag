# TaskAssistant Implementation Guide

## Overview

The TaskAssistant is a specialized component in the WhiteLabelRAG system that handles complex, multi-step task decomposition and execution. It serves as Layer 2 in the hierarchical workflow architecture, bridging the gap between the Concierge's high-level conversation management and the specialized Step Assistants' focused capabilities.

## Architecture Position

```
Layer 1: Concierge Agent (Main dialogue interface)
    ↓
Layer 2: TaskAssistant (Task decomposition and coordination) ← YOU ARE HERE
    ↓
Layer 3: Step Assistants (SearchAgent, FileAgent, FunctionAgent, MultimediaAgent)
```

## Core Components

### 1. TaskStep Class
Represents individual steps in a decomposed task.

```python
class TaskStep:
    def __init__(self, step_number, instruction, suggested_agent_type, dependencies=None):
        self.step_number = step_number
        self.instruction = instruction
        self.suggested_agent_type = suggested_agent_type
        self.dependencies = dependencies or []
        self.status = "pending"  # pending, running, completed, failed
        self.result = None
        self.retry_count = 0
        self.max_retries = 3
```

**Key Features:**
- **Dependency Management**: Steps can depend on completion of other steps
- **Retry Logic**: Failed steps can be retried up to a maximum count
- **Status Tracking**: Real-time status updates for monitoring
- **Agent Assignment**: Each step is assigned to the most appropriate specialized agent

### 2. Task Class
Represents a complete multi-step task.

```python
class Task:
    def __init__(self, task_id, original_request, user_session=None):
        self.task_id = task_id
        self.original_request = original_request
        self.steps = []
        self.status = "created"  # created, planning, executing, completed, failed
        self.execution_plan = None
```

**Key Features:**
- **Step Management**: Maintains ordered list of task steps
- **Execution Planning**: Stores analysis and execution strategy
- **Progress Tracking**: Overall task status and completion tracking
- **Session Context**: Links tasks to user sessions for context

### 3. TaskAssistant Class
Main orchestrator for task decomposition and execution.

## Task Decomposition Process

### 1. Task Analysis
The TaskAssistant first analyzes the incoming request to determine:
- **Complexity Level**: Simple, moderate, or complex
- **Required Capabilities**: Which types of agents will be needed
- **Estimated Duration**: How long the task might take
- **Resource Requirements**: What resources will be needed

### 2. Step Generation
Using an LLM with specialized prompting, the TaskAssistant breaks down the task:

```python
system_prompt = """
You are an expert task decomposition specialist. Break down the user's complex request into logical, executable steps.

For each step, determine:
1. A clear, specific instruction
2. The most appropriate agent type (SearchAgent, FileAgent, FunctionAgent, or MultimediaAgent)
3. Any dependencies on previous steps (by step number)
4. Estimated complexity (low, medium, high)

Guidelines:
- Keep steps atomic and focused
- Maximum 10 steps per task
- Use SearchAgent for information retrieval
- Use FileAgent for file operations
- Use FunctionAgent for calculations or API calls
- Use MultimediaAgent for media processing
- Consider dependencies carefully
"""
```

### 3. Dependency Resolution
The system automatically resolves step dependencies:
- **Parallel Execution**: Independent steps can run concurrently
- **Sequential Dependencies**: Steps that depend on others wait for completion
- **Circular Dependency Detection**: Prevents infinite loops

## Execution Workflow

### 1. Step Scheduling
```python
def get_ready_steps(self) -> List[TaskStep]:
    """Get steps that are ready to execute (dependencies completed)."""
    ready_steps = []
    completed_step_numbers = {step.step_number for step in self.steps if step.status == "completed"}
    
    for step in self.steps:
        if step.status == "pending":
            if all(dep in completed_step_numbers for dep in step.dependencies):
                ready_steps.append(step)
    
    return ready_steps
```

### 2. Agent Delegation
Each step is executed by the appropriate specialized agent:

```python
def _get_agent_for_step(self, step: TaskStep):
    """Get the appropriate agent instance for a step."""
    agent_type = step.suggested_agent_type
    
    if agent_type == "SearchAgent":
        from app.services.search_agent import get_search_agent_instance
        return get_search_agent_instance()
    elif agent_type == "FileAgent":
        from app.services.file_agent import get_file_agent_instance
        return get_file_agent_instance()
    # ... etc
```

### 3. Result Compilation
After all steps complete, results are synthesized:

```python
def _compile_final_result(self, task: Task, step_results: List[Dict[str, Any]]) -> str:
    """Compile final result from all step results."""
    # Use LLM to synthesize comprehensive response
    system_prompt = """
    You are a result synthesis specialist. Combine the results from multiple task steps 
    into a coherent, comprehensive final response.
    """
```

## Example Task Decomposition

### Input Task
"Analyze the uploaded climate report and create a summary with key findings and recommendations"

### Generated Steps
1. **Step 1** (FileAgent): List available uploaded files
2. **Step 2** (FileAgent): Read the climate report document
3. **Step 3** (SearchAgent): Extract key climate data and statistics
4. **Step 4** (SearchAgent): Identify main findings and conclusions
5. **Step 5** (FunctionAgent): Generate structured summary with recommendations

### Execution Flow
```
Step 1 → Step 2 → [Step 3, Step 4] → Step 5
         ↓         ↓                    ↑
    (Sequential)  (Parallel)      (Depends on 3&4)
```

## Error Handling and Recovery

### 1. Step-Level Retry
- Failed steps are automatically retried up to 3 times
- Exponential backoff between retries
- Different error types handled appropriately

### 2. Task-Level Fallback
- If critical steps fail, task can be marked as failed
- Partial results can still be returned
- Graceful degradation to simpler responses

### 3. Agent Unavailability
- If a specialized agent is unavailable, alternative approaches are attempted
- Fallback to general-purpose responses when needed

## Integration with Concierge

### 1. Intent Classification
The Concierge determines when to delegate to TaskAssistant:

```python
def _classify_intent(self, message: str, conversation) -> str:
    # Complex multi-step tasks are classified as "task_request"
    if intent == "task_request":
        return self._handle_task_decomposition(message, conversation)
```

### 2. Context Passing
Conversation context is passed to TaskAssistant:

```python
context = {
    'session_id': conversation.session_id,
    'conversation_context': conversation.get_context_string(500)
}
result = task_assistant.handle_message(message, context)
```

### 3. Result Integration
TaskAssistant results are seamlessly integrated into the conversation flow.

## Performance Considerations

### 1. Concurrent Execution
- Multiple independent steps can execute simultaneously
- Configurable concurrency limits prevent resource exhaustion
- Load balancing across available agent instances

### 2. Timeout Management
- Individual step timeouts prevent hanging operations
- Overall task timeouts ensure reasonable response times
- Graceful handling of timeout scenarios

### 3. Resource Management
- Memory-efficient step result storage
- Automatic cleanup of completed tasks
- Configurable retention policies

## Monitoring and Observability

### 1. Real-time Status Updates
- WebSocket notifications for step progress
- Detailed status information for debugging
- User-friendly progress indicators

### 2. Comprehensive Logging
- Step-by-step execution logs
- Performance metrics and timing
- Error tracking and analysis

### 3. Task Analytics
- Success/failure rates by task type
- Average execution times
- Resource utilization patterns

## Configuration Options

```python
config = {
    'max_steps': 10,              # Maximum steps per task
    'max_concurrent_steps': 3,    # Concurrent step execution limit
    'step_timeout': 300,          # Individual step timeout (seconds)
    'task_timeout': 1800,         # Overall task timeout (seconds)
    'max_retries': 3,             # Maximum retry attempts per step
    'cleanup_interval': 3600      # Task cleanup interval (seconds)
}
```

## Best Practices

### 1. Step Design
- Keep steps atomic and focused
- Minimize dependencies between steps
- Use clear, specific instructions
- Consider error scenarios

### 2. Agent Selection
- Choose the most appropriate agent for each step
- Consider agent capabilities and limitations
- Plan for agent unavailability

### 3. Result Synthesis
- Provide comprehensive final responses
- Maintain context throughout execution
- Include relevant sources and citations

## Future Enhancements

### 1. Dynamic Step Modification
- Ability to modify steps during execution
- Adaptive planning based on intermediate results
- User interaction during long-running tasks

### 2. Advanced Scheduling
- Priority-based step execution
- Resource-aware scheduling
- Cross-task optimization

### 3. Learning and Optimization
- Task pattern recognition
- Automatic optimization of decomposition strategies
- Performance-based agent selection