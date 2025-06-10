"""
Script to parse workflows for bottlenecks in delivery by analyzing TaskAssistant active tasks.
Identifies failed steps, blocked steps due to dependencies, and long-running tasks.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the root directory to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.task_assistant import get_task_assistant_instance

def parse_bottlenecks():
    task_assistant = get_task_assistant_instance()
    active_tasks = task_assistant.active_tasks
    
    bottlenecks = {
        'failed_steps': [],
        'blocked_tasks': [],
        'long_running_tasks': []
    }
    
    now = datetime.now()
    long_running_threshold = timedelta(minutes=10)  # Example threshold
    
    for task_id, task in active_tasks.items():
        # Check for failed steps
        for step in task.steps:
            if step.status == 'failed':
                bottlenecks['failed_steps'].append({
                    'task_id': task_id,
                    'step_number': step.step_number,
                    'instruction': step.instruction,
                    'error_message': step.error_message,
                    'retry_count': step.retry_count
                })
        
        # Check for blocked tasks (pending steps with unresolved dependencies)
        pending_steps = [s for s in task.steps if s.status == 'pending']
        ready_steps = task.get_ready_steps()
        if pending_steps and not ready_steps:
            bottlenecks['blocked_tasks'].append({
                'task_id': task_id,
                'pending_steps': [s.step_number for s in pending_steps],
                'reason': 'No ready steps due to unresolved dependencies or circular dependencies'
            })
        
        # Check for long running tasks
        if task.status == 'executing' and (now - task.created_at) > long_running_threshold:
            bottlenecks['long_running_tasks'].append({
                'task_id': task_id,
                'status': task.status,
                'created_at': task.created_at.isoformat(),
                'duration_seconds': (now - task.created_at).total_seconds(),
                'steps_completed': len([s for s in task.steps if s.status == 'completed']),
                'total_steps': len(task.steps)
            })
    
    return bottlenecks

if __name__ == "__main__":
    bottlenecks = parse_bottlenecks()
    print("Workflow Bottlenecks Report:")
    print("============================")
    print(f"Failed Steps: {len(bottlenecks['failed_steps'])}")
    for fs in bottlenecks['failed_steps']:
        print(f" - Task {fs['task_id']} Step {fs['step_number']}: {fs['instruction']} (Retries: {fs['retry_count']}) Error: {fs['error_message']}")
    
    print(f"\nBlocked Tasks: {len(bottlenecks['blocked_tasks'])}")
    for bt in bottlenecks['blocked_tasks']:
        print(f" - Task {bt['task_id']} Pending Steps: {bt['pending_steps']} Reason: {bt['reason']}")
    
    print(f"\nLong Running Tasks: {len(bottlenecks['long_running_tasks'])}")
    for lt in bottlenecks['long_running_tasks']:
        print(f" - Task {lt['task_id']} Duration: {lt['duration_seconds']}s Steps Completed: {lt['steps_completed']}/{lt['total_steps']}")
