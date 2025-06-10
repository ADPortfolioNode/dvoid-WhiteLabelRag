"""
TaskAssistant - Dedicated assistant for complex, multi-step task decomposition and execution
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.base_assistant import BaseAssistant
from app.services.llm_factory import LLMFactory
from app.config import Config

logger = logging.getLogger(__name__)

class TaskStep:
    """Represents a single step in a task decomposition."""
    
    def __init__(self, step_number: int, instruction: str, suggested_agent_type: str, 
                 dependencies: List[int] = None, metadata: Dict[str, Any] = None):
        self.step_number = step_number
        self.instruction = instruction
        self.suggested_agent_type = suggested_agent_type
        self.dependencies = dependencies or []
        self.metadata = metadata or {}
        self.status = "pending"  # pending, running, completed, failed
        self.result = None
        self.error_message = None
        self.created_at = datetime.now()
        self.completed_at = None
        self.retry_count = 0
        self.max_retries = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary."""
        return {
            "step_number": self.step_number,
            "instruction": self.instruction,
            "suggested_agent_type": self.suggested_agent_type,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "status": self.status,
            "result": self.result,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count
        }

class Task:
    """Represents a complete task with multiple steps."""
    
    def __init__(self, task_id: str, original_request: str, user_session: str = None):
        self.task_id = task_id
        self.original_request = original_request
        self.user_session = user_session
        self.steps: List[TaskStep] = []
        self.status = "created"  # created, planning, executing, completed, failed
        self.created_at = datetime.now()
        self.completed_at = None
        self.final_result = None
        self.execution_plan = None
    
    def add_step(self, step: TaskStep):
        """Add a step to the task."""
        self.steps.append(step)
    
    def get_ready_steps(self) -> List[TaskStep]:
        """Get steps that are ready to execute (dependencies completed)."""
        ready_steps = []
        completed_step_numbers = {step.step_number for step in self.steps if step.status == "completed"}
        
        for step in self.steps:
            if step.status == "pending":
                # Check if all dependencies are completed
                if all(dep in completed_step_numbers for dep in step.dependencies):
                    ready_steps.append(step)
        
        return ready_steps
    
    def is_completed(self) -> bool:
        """Check if all steps are completed."""
        return all(step.status in ["completed", "skipped"] for step in self.steps)
    
    def has_failed_steps(self) -> bool:
        """Check if any steps have failed."""
        return any(step.status == "failed" for step in self.steps)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "original_request": self.original_request,
            "user_session": self.user_session,
            "steps": [step.to_dict() for step in self.steps],
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "final_result": self.final_result,
            "execution_plan": self.execution_plan
        }

class TaskAssistant(BaseAssistant):
    """
    TaskAssistant - Handles complex, multi-step task decomposition and execution.
    
    This assistant implements Layer 2 of the hierarchical workflow architecture,
    breaking down complex tasks into logical steps and managing their execution
    through specialized Step Assistants.
    """
    
    def __init__(self):
        super().__init__("TaskAssistant")
        self.llm = LLMFactory.get_llm('reasoning')
        self.active_tasks: Dict[str, Task] = {}
        self.config = {
            'max_steps': 10,
            'max_concurrent_steps': 3,
            'step_timeout': 300,  # 5 minutes
            'task_timeout': 1800  # 30 minutes
        }
    
    def get_last_tasks(self, count: int = 3) -> List[Dict[str, Any]]:
        """Return the last 'count' tasks sorted by creation time descending."""
        # Sort tasks by created_at descending
        sorted_tasks = sorted(
            self.active_tasks.values(),
            key=lambda t: t.created_at,
            reverse=True
        )
        # Get the last 'count' tasks
        last_tasks = sorted_tasks[:count]
        # Convert to dict
        return [task.to_dict() for task in last_tasks]
    
    def handle_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle task decomposition and execution requests."""
        try:
            # Validate input
            is_valid, validation_message = self._validate_input(message)
            if not is_valid:
                return self.report_failure(validation_message)
            
            # Update status
            self._update_status("running", 10, "Analyzing task complexity...")
            
            # Create new task
            task_id = str(uuid.uuid4())
            user_session = context.get('session_id') if context else None
            task = Task(task_id, message, user_session)
            
            # Decompose task into steps
            self._update_status("running", 30, "Decomposing task into steps...")
            decomposition_result = self._decompose_task(task)
            
            if not decomposition_result['success']:
                return self.report_failure(f"Failed to decompose task: {decomposition_result['error']}")
            
            # Store task
            self.active_tasks[task_id] = task
            
            # Execute task
            self._update_status("running", 50, "Executing task steps...")
            execution_result = self._execute_task(task)
            
            if execution_result['success']:
                return self.report_success(
                    text=execution_result['result'],
                    additional_data={
                        'task_id': task_id,
                        'steps_completed': len([s for s in task.steps if s.status == "completed"]),
                        'total_steps': len(task.steps),
                        'execution_time': (datetime.now() - task.created_at).total_seconds()
                    }
                )
            else:
                return self.report_failure(f"Task execution failed: {execution_result['error']}")
            
        except Exception as e:
            logger.error(f"Error in TaskAssistant.handle_message: {str(e)}")
            return self.report_failure(f"Task processing error: {str(e)}")
    
    def _decompose_task(self, task: Task) -> Dict[str, Any]:
        """Decompose a complex task into logical steps."""
        try:
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
            
            Return a JSON structure with steps array.
            """
            
            prompt = f"""
            Task to decompose: {task.original_request}
            
            Please provide a step-by-step breakdown in this JSON format:
            {{
                "task_analysis": "Brief analysis of the task complexity and approach",
                "estimated_duration": "Estimated time in minutes",
                "steps": [
                    {{
                        "step_number": 1,
                        "instruction": "Specific instruction for this step",
                        "suggested_agent_type": "SearchAgent|FileAgent|FunctionAgent|MultimediaAgent",
                        "dependencies": [],
                        "complexity": "low|medium|high",
                        "estimated_time": "Estimated time in seconds"
                    }}
                ]
            }}
            """
            
            response = LLMFactory.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                task='reasoning'
            )
            
            # Parse the response
            import json
            try:
                decomposition = json.loads(response)
            except json.JSONDecodeError:
                # Fallback: extract JSON from response if it's wrapped in text
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    decomposition = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON response")
            
            # Validate decomposition
            if 'steps' not in decomposition or not decomposition['steps']:
                return {'success': False, 'error': 'No steps generated'}
            
            if len(decomposition['steps']) > self.config['max_steps']:
                return {'success': False, 'error': f'Too many steps (max {self.config["max_steps"]})'}
            
            # Create TaskStep objects
            for step_data in decomposition['steps']:
                step = TaskStep(
                    step_number=step_data['step_number'],
                    instruction=step_data['instruction'],
                    suggested_agent_type=step_data['suggested_agent_type'],
                    dependencies=step_data.get('dependencies', []),
                    metadata={
                        'complexity': step_data.get('complexity', 'medium'),
                        'estimated_time': step_data.get('estimated_time', 60)
                    }
                )
                task.add_step(step)
            
            # Store execution plan
            task.execution_plan = {
                'analysis': decomposition.get('task_analysis', ''),
                'estimated_duration': decomposition.get('estimated_duration', 'Unknown'),
                'total_steps': len(task.steps)
            }
            
            task.status = "planning"
            logger.info(f"Task {task.task_id} decomposed into {len(task.steps)} steps")
            
            return {'success': True, 'steps': len(task.steps)}
            
        except Exception as e:
            logger.error(f"Error decomposing task: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute all steps of a task."""
        try:
            task.status = "executing"
            step_results = []
            
            while not task.is_completed() and not task.has_failed_steps():
                # Get ready steps
                ready_steps = task.get_ready_steps()
                
                if not ready_steps:
                    if task.is_completed():
                        break
                    else:
                        # Check for circular dependencies or other issues
                        pending_steps = [s for s in task.steps if s.status == "pending"]
                        if pending_steps:
                            logger.error(f"Task {task.task_id} has pending steps but none are ready")
                            return {'success': False, 'error': 'Circular dependencies or unresolvable step dependencies'}
                        break
                
                # Execute ready steps (limit concurrent execution)
                steps_to_execute = ready_steps[:self.config['max_concurrent_steps']]
                
                for step in steps_to_execute:
                    step_result = self._execute_step(step, task)
                    step_results.append(step_result)
                    
                    if not step_result['success'] and step.retry_count >= step.max_retries:
                        step.status = "failed"
                        step.error_message = step_result['error']
                        logger.error(f"Step {step.step_number} failed permanently: {step_result['error']}")
                        break
            
            # Compile final result
            if task.has_failed_steps():
                task.status = "failed"
                failed_steps = [s for s in task.steps if s.status == "failed"]
                error_msg = f"Task failed. Failed steps: {[s.step_number for s in failed_steps]}"
                return {'success': False, 'error': error_msg}
            
            elif task.is_completed():
                task.status = "completed"
                task.completed_at = datetime.now()
                
                # Generate final result summary
                final_result = self._compile_final_result(task, step_results)
                task.final_result = final_result
                
                return {'success': True, 'result': final_result}
            
            else:
                return {'success': False, 'error': 'Task execution incomplete for unknown reason'}
            
        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {str(e)}")
            task.status = "failed"
            return {'success': False, 'error': str(e)}
    
    def _execute_step(self, step: TaskStep, task: Task) -> Dict[str, Any]:
        """Execute a single step using the appropriate agent."""
        try:
            step.status = "running"
            logger.info(f"Executing step {step.step_number}: {step.instruction}")
            
            # Get the appropriate agent
            agent = self._get_agent_for_step(step)
            if not agent:
                return {'success': False, 'error': f'No agent available for type: {step.suggested_agent_type}'}
            
            # Execute step
            result = agent.handle_message(step.instruction)
            
            if result.get('error') or not result.get('success', True):
                step.retry_count += 1
                if step.retry_count < step.max_retries:
                    step.status = "pending"  # Retry
                    return {'success': False, 'error': result.get('text', 'Step execution failed'), 'retry': True}
                else:
                    step.status = "failed"
                    step.error_message = result.get('text', 'Step execution failed')
                    return {'success': False, 'error': step.error_message}
            else:
                step.status = "completed"
                step.completed_at = datetime.now()
                step.result = result.get('text', '')
                return {'success': True, 'result': step.result}
            
        except Exception as e:
            logger.error(f"Error executing step {step.step_number}: {str(e)}")
            step.retry_count += 1
            if step.retry_count < step.max_retries:
                step.status = "pending"
                return {'success': False, 'error': str(e), 'retry': True}
            else:
                step.status = "failed"
                step.error_message = str(e)
                return {'success': False, 'error': str(e)}
    
    def _get_agent_for_step(self, step: TaskStep):
        """Get the appropriate agent instance for a step."""
        try:
            agent_type = step.suggested_agent_type
            
            if agent_type == "SearchAgent":
                from app.services.search_agent import get_search_agent_instance
                return get_search_agent_instance()
            elif agent_type == "FileAgent":
                from app.services.file_agent import get_file_agent_instance
                return get_file_agent_instance()
            elif agent_type == "FunctionAgent":
                from app.services.function_agent import get_function_agent_instance
                return get_function_agent_instance()
            elif agent_type == "MultimediaAgent":
                from app.services.multimedia_agent import get_multimedia_agent_instance
                return get_multimedia_agent_instance()
            else:
                logger.error(f"Unknown agent type: {agent_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting agent for step: {str(e)}")
            return None
    
    def _compile_final_result(self, task: Task, step_results: List[Dict[str, Any]]) -> str:
        """Compile final result from all step results."""
        try:
            # Collect all step results
            completed_steps = [s for s in task.steps if s.status == "completed"]
            
            if not completed_steps:
                return "Task completed but no results were generated."
            
            # Use LLM to synthesize final result
            system_prompt = """
            You are a result synthesis specialist. Combine the results from multiple task steps into a coherent, comprehensive final response.
            
            Guidelines:
            - Synthesize information from all steps
            - Maintain logical flow and coherence
            - Include key findings and conclusions
            - Be concise but complete
            - Cite step numbers when referencing specific results
            """
            
            step_summaries = []
            for step in completed_steps:
                step_summaries.append(f"Step {step.step_number} ({step.suggested_agent_type}): {step.instruction}\nResult: {step.result}")
            
            prompt = f"""
            Original task: {task.original_request}
            
            Step results:
            {chr(10).join(step_summaries)}
            
            Please provide a comprehensive final response that addresses the original task using the information from all completed steps.
            """
            
            final_result = LLMFactory.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2,
                task='reasoning'
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error compiling final result: {str(e)}")
            # Fallback: simple concatenation
            results = [f"Step {s.step_number}: {s.result}" for s in completed_steps]
            return f"Task completed with {len(completed_steps)} steps:\n\n" + "\n\n".join(results)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].to_dict()
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = "cancelled"
            # Mark running steps as cancelled
            for step in task.steps:
                if step.status == "running":
                    step.status = "cancelled"
            return True
        return False
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks."""
        current_time = datetime.now()
        tasks_to_remove = []
        
        for task_id, task in self.active_tasks.items():
            if task.status in ["completed", "failed", "cancelled"]:
                age = current_time - task.created_at
                if age.total_seconds() > max_age_hours * 3600:
                    tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.active_tasks[task_id]
            logger.info(f"Cleaned up old task: {task_id}")

# Singleton instance
_task_assistant_instance = None

def get_task_assistant_instance() -> TaskAssistant:
    """Get the singleton TaskAssistant instance."""
    global _task_assistant_instance
    if _task_assistant_instance is None:
        _task_assistant_instance = TaskAssistant()
    return _task_assistant_instance