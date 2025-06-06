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
from app.config import Config

logger = logging.getLogger(__name__)

class FunctionAgent(BaseAssistant):
    """
    FunctionAgent - Specialized for function execution and API integrations.
    Handles API calling, function execution, data transformation, and external service integration.
    """
    
    def __init__(self):
        super().__init__("FunctionAgent")
        self.config = Config.ASSISTANT_CONFIGS['FunctionAgent']
        self.llm = LLMFactory.get_llm()
        
        # Available functions registry
        self.available_functions = {
            'get_current_time': self._get_current_time,
            'calculate': self._calculate,
            'format_data': self._format_data,
            'validate_json': self._validate_json,
            'make_http_request': self._make_http_request,
            'transform_text': self._transform_text,
            'generate_uuid': self._generate_uuid,
            'encode_decode': self._encode_decode,
            'date_operations': self._date_operations
        }
    
    def handle_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle function execution requests."""
        try:
            # Validate input
            is_valid, validation_message = self._validate_input(message)
            if not is_valid:
                return self.report_failure(validation_message)
            
            # Update status
            self._update_status("running", 10, "Analyzing function request...")
            
            # Extract function call from message
            function_call = self._extract_function_call(message)
            
            if not function_call:
                return self._provide_function_help()
            
            function_name = function_call.get('name')
            parameters = function_call.get('parameters', {})
            
            # Validate function exists
            if function_name not in self.available_functions:
                return self.report_failure(f"Function '{function_name}' is not available. Use 'list functions' to see available functions.")
            
            # Execute function
            self._update_status("running", 50, f"Executing {function_name}...")
            result = self._execute_function(function_call)
            
            return self.report_success(
                text=result,
                additional_data={
                    'function_executed': function_name,
                    'parameters_used': parameters
                }
            )
            
        except Exception as e:
            logger.error(f"Error in FunctionAgent.handle_message: {str(e)}")
            return self.report_failure(f"Function execution error: {str(e)}")
    
    def _extract_function_call(self, message: str) -> Dict[str, Any]:
        """Extract function call information from message using LLM."""
        try:
            system_prompt = f"""
            Analyze the user's message and extract function call information.
            Available functions: {', '.join(self.available_functions.keys())}
            
            If the message contains a function request, return a JSON object with:
            {{
                "name": "function_name",
                "parameters": {{"param1": "value1", "param2": "value2"}}
            }}
            
            If no function call is detected, return null.
            
            Function descriptions:
            - get_current_time: Get current date and time
            - calculate: Perform mathematical calculations
            - format_data: Format data in various ways
            - validate_json: Validate JSON strings
            - make_http_request: Make HTTP requests to APIs
            - transform_text: Transform text (uppercase, lowercase, etc.)
            - generate_uuid: Generate unique identifiers
            - encode_decode: Encode/decode text (base64, URL encoding, etc.)
            - date_operations: Perform date calculations and formatting
            """
            
            response = LLMFactory.generate_response(
                prompt=message,
                system_prompt=system_prompt,
                temperature=0.1
            )
            
            # Try to parse JSON response
            try:
                function_call = json.loads(response.strip())
                return function_call if function_call else None
            except json.JSONDecodeError:
                # If not JSON, try to extract function name manually
                return self._manual_function_extraction(message)
                
        except Exception as e:
            logger.error(f"Error extracting function call: {str(e)}")
            return self._manual_function_extraction(message)
    
    def _manual_function_extraction(self, message: str) -> Dict[str, Any]:
        """Manually extract function information from message."""
        message_lower = message.lower()
        
        # Check for specific function patterns
        if 'time' in message_lower or 'date' in message_lower:
            if 'current' in message_lower or 'now' in message_lower:
                return {'name': 'get_current_time', 'parameters': {}}
            else:
                return {'name': 'date_operations', 'parameters': {'operation': message}}
        
        elif any(word in message_lower for word in ['calculate', 'math', 'compute', '+', '-', '*', '/']):
            return {'name': 'calculate', 'parameters': {'expression': message}}
        
        elif 'uuid' in message_lower or 'unique id' in message_lower:
            return {'name': 'generate_uuid', 'parameters': {}}
        
        elif any(word in message_lower for word in ['format', 'transform', 'convert']):
            if 'json' in message_lower:
                return {'name': 'validate_json', 'parameters': {'json_string': message}}
            elif any(word in message_lower for word in ['upper', 'lower', 'title']):
                return {'name': 'transform_text', 'parameters': {'text': message, 'operation': 'auto'}}
            else:
                return {'name': 'format_data', 'parameters': {'data': message}}
        
        elif any(word in message_lower for word in ['encode', 'decode', 'base64', 'url']):
            return {'name': 'encode_decode', 'parameters': {'text': message, 'operation': 'auto'}}
        
        elif any(word in message_lower for word in ['http', 'api', 'request', 'get', 'post']):
            return {'name': 'make_http_request', 'parameters': {'description': message}}
        
        return None
    
    def _execute_function(self, function_call: Dict[str, Any]) -> str:
        """Execute the specified function with parameters."""
        function_name = function_call.get('name')
        parameters = function_call.get('parameters', {})
        
        if function_name not in self.available_functions:
            return f"Function '{function_name}' not found."
        
        try:
            function = self.available_functions[function_name]
            result = function(**parameters)
            return str(result)
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {str(e)}")
            return f"Error executing {function_name}: {str(e)}"
    
    def _get_current_time(self) -> str:
        """Get current date and time."""
        now = datetime.now()
        return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')} ({now.strftime('%A, %B %d, %Y')})"
    
    def _calculate(self, expression: str = "", **kwargs) -> str:
        """Perform mathematical calculations."""
        try:
            # Extract mathematical expression from the input
            import re
            
            # Clean the expression
            if not expression:
                expression = kwargs.get('operation', '')
            
            # Simple math expression extraction
            math_pattern = r'[\d+\-*/().\s]+'
            matches = re.findall(math_pattern, expression)
            
            if matches:
                expr = ''.join(matches).strip()
                # Basic safety check
                if any(char in expr for char in ['import', 'exec', 'eval', '__']):
                    return "Invalid expression for security reasons."
                
                try:
                    result = eval(expr)
                    return f"Result: {expr} = {result}"
                except:
                    return f"Could not evaluate expression: {expr}"
            
            return "No valid mathematical expression found."
            
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    def _format_data(self, data: str = "", format_type: str = "auto", **kwargs) -> str:
        """Format data in various ways."""
        try:
            if not data:
                data = str(kwargs)
            
            if format_type == "json" or "json" in data.lower():
                try:
                    # Try to parse and pretty-print JSON
                    parsed = json.loads(data)
                    return f"Formatted JSON:\n{json.dumps(parsed, indent=2)}"
                except:
                    return "Invalid JSON format."
            
            elif format_type == "list" or isinstance(data, str) and ',' in data:
                items = [item.strip() for item in data.split(',')]
                return f"Formatted list:\n" + "\n".join(f"• {item}" for item in items)
            
            else:
                # Default formatting
                return f"Formatted data:\n{data}"
                
        except Exception as e:
            return f"Formatting error: {str(e)}"
    
    def _validate_json(self, json_string: str = "", **kwargs) -> str:
        """Validate JSON strings."""
        try:
            if not json_string:
                json_string = kwargs.get('data', '')
            
            # Extract JSON from the string if it's embedded
            import re
            json_pattern = r'\{.*\}|\[.*\]'
            matches = re.findall(json_pattern, json_string, re.DOTALL)
            
            if matches:
                json_string = matches[0]
            
            parsed = json.loads(json_string)
            return f"✅ Valid JSON!\nParsed structure:\n{json.dumps(parsed, indent=2)}"
            
        except json.JSONDecodeError as e:
            return f"❌ Invalid JSON: {str(e)}"
        except Exception as e:
            return f"Validation error: {str(e)}"
    
    def _make_http_request(self, url: str = "", method: str = "GET", description: str = "", **kwargs) -> str:
        """Make HTTP requests to APIs."""
        try:
            # For security, only allow specific domains or require explicit approval
            if not url and description:
                return f"HTTP request description received: {description}\nNote: For security reasons, actual HTTP requests are restricted. Please provide specific, approved URLs."
            
            if url:
                # Basic URL validation
                if not url.startswith(('http://', 'https://')):
                    return "Invalid URL format. Must start with http:// or https://"
                
                # For demo purposes, simulate the request
                return f"Simulated {method} request to {url}\nNote: Actual HTTP requests are restricted for security."
            
            return "No URL provided for HTTP request."
            
        except Exception as e:
            return f"HTTP request error: {str(e)}"
    
    def _transform_text(self, text: str = "", operation: str = "auto", **kwargs) -> str:
        """Transform text in various ways."""
        try:
            if not text:
                text = kwargs.get('input', '')
            
            # Extract actual text to transform
            if operation == "auto":
                text_lower = text.lower()
                if 'upper' in text_lower:
                    operation = "uppercase"
                    # Extract text after "upper"
                    parts = text.split()
                    if len(parts) > 1:
                        text = ' '.join(parts[1:])
                elif 'lower' in text_lower:
                    operation = "lowercase"
                    parts = text.split()
                    if len(parts) > 1:
                        text = ' '.join(parts[1:])
                elif 'title' in text_lower:
                    operation = "title"
                    parts = text.split()
                    if len(parts) > 1:
                        text = ' '.join(parts[1:])
                else:
                    operation = "info"
            
            if operation == "uppercase":
                return f"Uppercase: {text.upper()}"
            elif operation == "lowercase":
                return f"Lowercase: {text.lower()}"
            elif operation == "title":
                return f"Title Case: {text.title()}"
            elif operation == "reverse":
                return f"Reversed: {text[::-1]}"
            elif operation == "info":
                return f"Text info:\nLength: {len(text)} characters\nWords: {len(text.split())} words\nLines: {len(text.splitlines())} lines"
            else:
                return f"Available operations: uppercase, lowercase, title, reverse, info\nText: {text}"
                
        except Exception as e:
            return f"Text transformation error: {str(e)}"
    
    def _generate_uuid(self, version: int = 4, **kwargs) -> str:
        """Generate unique identifiers."""
        try:
            import uuid
            
            if version == 1:
                new_uuid = uuid.uuid1()
            elif version == 4:
                new_uuid = uuid.uuid4()
            else:
                new_uuid = uuid.uuid4()
            
            return f"Generated UUID (v{version}): {str(new_uuid)}"
            
        except Exception as e:
            return f"UUID generation error: {str(e)}"
    
    def _encode_decode(self, text: str = "", operation: str = "auto", encoding: str = "base64", **kwargs) -> str:
        """Encode/decode text in various formats."""
        try:
            if not text:
                text = kwargs.get('input', '')
            
            # Determine operation
            if operation == "auto":
                text_lower = text.lower()
                if 'encode' in text_lower:
                    operation = "encode"
                elif 'decode' in text_lower:
                    operation = "decode"
                else:
                    operation = "encode"  # default
            
            # Determine encoding type
            if 'base64' in text.lower():
                encoding = "base64"
            elif 'url' in text.lower():
                encoding = "url"
            
            if encoding == "base64":
                import base64
                if operation == "encode":
                    encoded = base64.b64encode(text.encode()).decode()
                    return f"Base64 encoded: {encoded}"
                else:
                    try:
                        decoded = base64.b64decode(text).decode()
                        return f"Base64 decoded: {decoded}"
                    except:
                        return "Invalid base64 string for decoding."
            
            elif encoding == "url":
                import urllib.parse
                if operation == "encode":
                    encoded = urllib.parse.quote(text)
                    return f"URL encoded: {encoded}"
                else:
                    decoded = urllib.parse.unquote(text)
                    return f"URL decoded: {decoded}"
            
            return f"Supported encodings: base64, url\nOperation: {operation}\nText: {text}"
            
        except Exception as e:
            return f"Encoding/decoding error: {str(e)}"
    
    def _date_operations(self, operation: str = "", date_string: str = "", **kwargs) -> str:
        """Perform date calculations and formatting."""
        try:
            from datetime import datetime, timedelta
            import re
            
            now = datetime.now()
            
            if not operation:
                operation = kwargs.get('input', '')
            
            operation_lower = operation.lower()
            
            # Parse different date operations
            if 'tomorrow' in operation_lower:
                tomorrow = now + timedelta(days=1)
                return f"Tomorrow: {tomorrow.strftime('%Y-%m-%d %H:%M:%S')} ({tomorrow.strftime('%A, %B %d, %Y')})"
            
            elif 'yesterday' in operation_lower:
                yesterday = now - timedelta(days=1)
                return f"Yesterday: {yesterday.strftime('%Y-%m-%d %H:%M:%S')} ({yesterday.strftime('%A, %B %d, %Y')})"
            
            elif 'week' in operation_lower:
                if 'next' in operation_lower:
                    next_week = now + timedelta(weeks=1)
                    return f"Next week: {next_week.strftime('%Y-%m-%d')} ({next_week.strftime('%A, %B %d, %Y')})"
                elif 'last' in operation_lower:
                    last_week = now - timedelta(weeks=1)
                    return f"Last week: {last_week.strftime('%Y-%m-%d')} ({last_week.strftime('%A, %B %d, %Y')})"
            
            elif 'days' in operation_lower:
                # Extract number of days
                numbers = re.findall(r'\d+', operation)
                if numbers:
                    days = int(numbers[0])
                    if 'ago' in operation_lower or 'before' in operation_lower:
                        target_date = now - timedelta(days=days)
                        return f"{days} days ago: {target_date.strftime('%Y-%m-%d')} ({target_date.strftime('%A, %B %d, %Y')})"
                    else:
                        target_date = now + timedelta(days=days)
                        return f"In {days} days: {target_date.strftime('%Y-%m-%d')} ({target_date.strftime('%A, %B %d, %Y')})"
            
            # Default: return current date in various formats
            return f"""Current date and time:
• Standard: {now.strftime('%Y-%m-%d %H:%M:%S')}
• Full: {now.strftime('%A, %B %d, %Y at %I:%M %p')}
• ISO: {now.isoformat()}
• Timestamp: {int(now.timestamp())}
• Day of year: {now.timetuple().tm_yday}
• Week number: {now.isocalendar()[1]}"""
            
        except Exception as e:
            return f"Date operation error: {str(e)}"
    
    def _provide_function_help(self) -> Dict[str, Any]:
        """Provide help information about available functions."""
        help_text = """🔧 **Function Execution Help**

I can execute the following functions:

⏰ **Time & Date Functions:**
• `get_current_time` - Get current date and time
• `date_operations` - Calculate dates (tomorrow, yesterday, in X days, etc.)

🧮 **Calculation Functions:**
• `calculate` - Perform mathematical calculations
• `format_data` - Format data in various ways (JSON, lists, etc.)

🔤 **Text Functions:**
• `transform_text` - Transform text (uppercase, lowercase, title case, etc.)
• `encode_decode` - Encode/decode text (base64, URL encoding)

🔧 **Utility Functions:**
• `generate_uuid` - Generate unique identifiers
• `validate_json` - Validate JSON strings
• `make_http_request` - Make HTTP requests (restricted for security)

**Examples:**
• "What time is it?"
• "Calculate 15 * 23 + 7"
• "Convert 'hello world' to uppercase"
• "Generate a UUID"
• "What's the date tomorrow?"
• "Encode 'secret message' in base64"
• "Validate this JSON: {'name': 'test'}"

Just describe what you want to do naturally!
"""
        
        return self.report_success(help_text)
    
    def list_available_functions(self) -> List[str]:
        """Get list of available function names."""
        return list(self.available_functions.keys())
    
    def get_function_info(self, function_name: str) -> Dict[str, Any]:
        """Get information about a specific function."""
        if function_name not in self.available_functions:
            return {'error': f"Function '{function_name}' not found"}
        
        # This could be enhanced with actual function documentation
        function_docs = {
            'get_current_time': {
                'description': 'Get current date and time',
                'parameters': [],
                'example': 'What time is it?'
            },
            'calculate': {
                'description': 'Perform mathematical calculations',
                'parameters': ['expression'],
                'example': 'Calculate 15 * 23 + 7'
            },
            'format_data': {
                'description': 'Format data in various ways',
                'parameters': ['data', 'format_type'],
                'example': 'Format this as JSON: name=test, age=25'
            },
            'validate_json': {
                'description': 'Validate JSON strings',
                'parameters': ['json_string'],
                'example': 'Validate this JSON: {"name": "test"}'
            },
            'make_http_request': {
                'description': 'Make HTTP requests (restricted)',
                'parameters': ['url', 'method'],
                'example': 'Make a GET request to example.com'
            },
            'transform_text': {
                'description': 'Transform text in various ways',
                'parameters': ['text', 'operation'],
                'example': 'Convert "hello world" to uppercase'
            },
            'generate_uuid': {
                'description': 'Generate unique identifiers',
                'parameters': ['version'],
                'example': 'Generate a UUID'
            },
            'encode_decode': {
                'description': 'Encode/decode text',
                'parameters': ['text', 'operation', 'encoding'],
                'example': 'Encode "secret" in base64'
            },
            'date_operations': {
                'description': 'Perform date calculations',
                'parameters': ['operation'],
                'example': 'What is the date tomorrow?'
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