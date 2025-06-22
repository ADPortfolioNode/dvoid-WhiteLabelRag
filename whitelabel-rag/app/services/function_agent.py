"""
FunctionAgent - Specialized for function execution and API integrations
"""

import logging
import json
import requests
from datetime import datetime
from typing import Dict, Any, List, Callable
from app.services.base_assistant import BaseAssistant
from app.services.llm_factory import LLMFactory

logger = logging.getLogger(__name__)

class FunctionAgent(BaseAssistant):
    """
    FunctionAgent - Specialized for function execution and API integrations.
    Handles API calling, function execution, data transformation, and external service integration.
    """
    
    def __init__(self):
        super().__init__("FunctionAgent")
        self.llm = LLMFactory.get_llm()
        self.available_functions = {
            "calculate": self._calculate,
            "uppercase": self._uppercase,
            # Add more functions as needed
        }

    def handle_message(self, message):
        function_call = self._extract_function_call(message)
        if function_call and function_call["name"] in self.available_functions:
            result = self.available_functions[function_call["name"]](function_call.get("args", ""))
            return self.report_success(text=result)
        else:
            return self.report_failure("No valid function call could be extracted from the request.")

    def _extract_function_call(self, message):
        # Simple pattern matching for demo
        if "calculate" in message.lower():
            expr = message.lower().replace("calculate", "").strip()
            return {"name": "calculate", "args": expr}
        if "uppercase" in message.lower():
            text = message.lower().replace("uppercase", "").strip()
            return {"name": "uppercase", "args": text}
        return None

    def _calculate(self, expr):
        try:
            result = eval(expr, {"__builtins__": {}})
            return f"Result: {result}"
        except Exception:
            return "Invalid calculation."

    def _uppercase(self, text):
        return text.upper()
    
    def list_available_functions(self) -> List[str]:
        """Get list of available function names."""
        return list(self.available_functions.keys())
    
    def get_function_info(self, function_name: str) -> Dict[str, Any]:
        """Get information about a specific function."""
        if function_name not in self.available_functions:
            return {'error': f"Function '{function_name}' not found"}
        
        # This could be enhanced with actual function documentation
        function_docs = {
            'calculate': {
                'description': 'Perform mathematical calculations',
                'parameters': ['expression'],
                'example': 'Calculate 15 * 23 + 7'
            },
            'uppercase': {
                'description': 'Convert text to uppercase',
                'parameters': ['text'],
                'example': 'Convert "hello world" to uppercase'
            }
        }
        
        return function_docs.get(function_name, {'description': 'No documentation available'})

# Singleton instance
_function_agent_instance = None

def get_function_agent_instance() -> FunctionAgent:
    """Get the singleton FunctionAgent instance."""
    global _function_agent_instance
    if _function_agent_instance is None:
        _function_agent_instance = FunctionAgent()
    return _function_agent_instance