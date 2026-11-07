"""
LLM Factory for creating and managing language model instances
"""

import os
import logging
import google.generativeai as genai
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class LLMFactory:
    """Factory class for creating and managing LLM instances."""
    
    _instance = None
    _llm = None
    _available_models = None
    _model_assignments = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMFactory, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._setup_gemini()
    
    def _setup_gemini(self):
        """Setup Google Gemini API."""
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            error_msg = (
                "GEMINI_API_KEY environment variable is required but not found. "
                "Please set it as an environment variable or add it to your .env file. "
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            genai.configure(api_key=api_key)
            
            # Get available models
            self._available_models = self._get_available_models()
            
            # Assign appropriate models for different tasks
            self._assign_models()
            
            # Set default LLM
            default_model = self._get_best_model_for_task('general')
            self._llm = genai.GenerativeModel(default_model)
            logger.info(f"✅ Gemini API configured successfully with model: {default_model}")
            
        except Exception as e:
            error_msg = f"Error configuring Gemini API: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _get_available_models(self) -> List[str]:
        """Fetch available Gemini models from the API."""
        try:
            models = []
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    models.append(model.name)
            
            logger.info(f"Available Gemini models: {models}")
            return models
            
        except Exception as e:
            logger.warning(f"Could not fetch available models: {str(e)}")
            # Fallback to known models
            fallback_models = [
                'models/gemini-1.5-flash',
                'models/gemini-1.5-pro',
                'models/gemini-pro',
                'models/gemini-1.0-pro'
            ]
            logger.info(f"Using fallback models: {fallback_models}")
            return fallback_models
    
    def _assign_models(self):
        """Assign appropriate models for different tasks based on availability."""
        if not self._available_models:
            return
        
        # Model preferences for different tasks
        model_preferences = {
            'general': ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro', 'models/gemini-1.0-pro'],
            'reasoning': ['models/gemini-1.5-pro', 'models/gemini-pro', 'models/gemini-1.5-flash', 'models/gemini-1.0-pro'],
            'fast': ['models/gemini-1.5-flash', 'models/gemini-pro', 'models/gemini-1.5-pro', 'models/gemini-1.0-pro'],
            'embedding': ['models/embedding-001', 'models/text-embedding-004'],
            'search': ['models/gemini-1.5-flash', 'models/gemini-pro', 'models/gemini-1.5-pro'],
            'classification': ['models/gemini-1.5-flash', 'models/gemini-pro', 'models/gemini-1.5-pro']
        }
        
        # Assign best available model for each task
        for task, preferences in model_preferences.items():
            assigned_model = None
            for preferred_model in preferences:
                if preferred_model in self._available_models:
                    assigned_model = preferred_model
                    break
            
            if assigned_model:
                self._model_assignments[task] = assigned_model
                logger.info(f"Assigned {assigned_model} for {task} tasks")
            else:
                # Use first available model as fallback
                if self._available_models:
                    self._model_assignments[task] = self._available_models[0]
                    logger.warning(f"No preferred model found for {task}, using {self._available_models[0]}")
    
    def _get_best_model_for_task(self, task: str) -> str:
        """Get the best available model for a specific task."""
        return self._model_assignments.get(task, self._available_models[0] if self._available_models else 'models/gemini-pro')
    
    @classmethod
    def get_llm(cls, task: str = 'general'):
        """Get the LLM instance for a specific task."""
        instance = cls()
        if task != 'general':
            model_name = instance._get_best_model_for_task(task)
            return genai.GenerativeModel(model_name)
        return instance._llm
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get list of available models."""
        instance = cls()
        return instance._available_models or []
    
    @classmethod
    def get_model_assignments(cls) -> Dict[str, str]:
        """Get current model assignments for different tasks."""
        instance = cls()
        return instance._model_assignments.copy()
    
    @classmethod
    def generate_response(cls, prompt: str, system_prompt: Optional[str] = None,
                         temperature: float = 0.2, max_tokens: int = 1024,
                         task: str = 'general') -> str:
        """Generate a response via the multi-provider fallback chain.

        Tries Gemini, then Groq, then Ollama. When every LLM rung fails
        or is unconfigured, falls back to the retrieved text carried in
        the prompt instead of returning an error string.
        ChainLLM.last_provider records which rung answered; see
        /api/llm/status.
        """
        from app.services.chain_llm import ChainLLM

        try:
            text, _provider = ChainLLM.generate(
                prompt, system_prompt, temperature, max_tokens, task)
        except Exception as e:  # noqa: BLE001 - the chain must never raise
            logger.error(f"Error generating response: {str(e)}")
            text = None
        if text:
            return text
        return cls._retrieved_text_fallback(prompt)

    @classmethod
    def _retrieved_text_fallback(cls, prompt: str) -> str:
        """Last chain rung: the retrieved documents themselves.

        rag_manager builds prompts as "Context:\\n{context}\\n\\nQuestion:
        {query}", so the context can be recovered from the prompt. When
        no context is present, say plainly that no provider answered.
        """
        context = ""
        marker = "Context:\n"
        if marker in prompt:
            rest = prompt.split(marker, 1)[1]
            if "\n\nQuestion:" in rest:
                context = rest.split("\n\nQuestion:", 1)[0].strip()
            else:
                context = rest.strip()
        if context:
            return (
                "[No LLM provider was available, so here are the retrieved "
                "documents instead:]\n\n" + context
            )
        return (
            "No LLM provider was available to answer this question. "
            "Check /api/llm/status and make sure at least one provider "
            "key is set (GEMINI_API_KEY, GROQ_API_KEY, or the others)."
        )
    
    @classmethod
    def generate_structured_response(cls, prompt: str, context: str = "", 
                                   sources: list = None, system_prompt: str = None,
                                   task: str = 'general') -> Dict[str, Any]:
        """Generate a structured response with context and sources."""
        try:
            from datetime import datetime
            
            # Build the full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
            
            # Generate response
            response_text = cls.generate_response(full_prompt, system_prompt, task=task)

            from app.services.chain_llm import ChainLLM

            return {
                'text': response_text,
                'sources': sources or [],
                'context_used': bool(context),
                'provider': ChainLLM.last_provider,
                'timestamp': str(datetime.now())
            }

        except Exception as e:
            logger.error(f"Error generating structured response: {str(e)}")
            from datetime import datetime
            return {
                'text': f"Error generating response: {str(e)}",
                'sources': [],
                'context_used': False,
                'provider': None,
                'error': True,
                'timestamp': str(datetime.now())
            }
    
    @classmethod
    def classify_intent(cls, message: str) -> str:
        """Classify user message intent using LLM."""
        try:
            system_prompt = """
            Classify the user's message into one of these categories:
            - simple_query: Direct question answerable from context
            - document_search: Request to find information in documents
            - task_request: Multi-step task requiring decomposition
            - clarification: User asking for clarification or followup
            - feedback: User providing feedback on previous response
            - meta: Question about the system itself
            
            Respond with only the category name.
            """
            
            response = cls.generate_response(message, system_prompt, temperature=0.1, task='classification')
            return response.strip().lower()
            
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            return "simple_query"  # Default fallback

from datetime import datetime