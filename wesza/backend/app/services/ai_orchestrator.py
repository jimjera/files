"""
AI Orchestrator service for Groq API integration.

This module provides the core AI orchestration functionality including:
- Intent classification using Llama models
- JSON config generation using GPT-OSS
- Code generation with model routing based on complexity
- Rate limit handling with exponential backoff
"""

import structlog
import asyncio
from typing import Any, Dict, List, Optional
from groq import AsyncGroq

from app.config import settings

logger = structlog.get_logger()


class AIOrchestrator:
    """
    AI Orchestrator for managing Groq API interactions.
    
    This class handles all AI model interactions including intent
    classification, template generation, and code generation with
    proper error handling and rate limit management.
    
    Attributes:
        client: Async Groq client instance.
    """
    
    # Model IDs for different tasks
    INTENT_MODEL = "llama-3.1-8b-instant"
    CONFIG_MODEL = "openai/gpt-oss-20b"
    SIMPLE_CODE_MODEL = "openai/gpt-oss-20b"
    COMPLEX_CODE_MODEL = "llama-3.3-70b-versatile"
    
    def __init__(self):
        """Initialize AI Orchestrator with Groq client."""
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        logger.debug("AI Orchestrator initialized")
    
    async def _make_request(
        self,
        model: str,
        messages: List[Dict[str, str]],
        response_format: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
    ) -> Optional[str]:
        """
        Make a request to Groq API with retry logic.
        
        Args:
            model: Model ID to use.
            messages: Chat completion messages.
            response_format: Optional response format specification.
            max_retries: Maximum number of retry attempts.
            
        Returns:
            Optional[str]: Response content or None if failed.
        """
        attempt = 0
        base_delay = 1.0
        
        while attempt < max_retries:
            try:
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "timeout": 30,
                }
                
                if response_format:
                    kwargs["response_format"] = response_format
                
                response = await self.client.chat.completions.create(**kwargs)
                
                if not response.choices or not response.choices[0].message.content:
                    logger.warning("Empty response from AI model", model=model)
                    return None
                
                return response.choices[0].message.content
            
            except Exception as e:
                attempt += 1
                
                # Check if rate limited
                if "429" in str(e) or "rate limit" in str(e).lower():
                    delay = base_delay * (2 ** (attempt - 1))  # Exponential backoff
                    logger.warning(
                        "Rate limited, retrying",
                        model=model,
                        attempt=attempt,
                        delay=delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "AI request failed",
                        model=model,
                        error=str(e),
                        attempt=attempt,
                    )
                    
                    if attempt >= max_retries:
                        return None
                    
                    await asyncio.sleep(base_delay)
        
        return None
    
    async def classify_intent(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Classify user intent from natural language prompt.
        
        Uses Llama-3.1-8b-instant for fast, cheap intent classification.
        
        Args:
            prompt: User's natural language description.
            
        Returns:
            Optional[Dict]: Classification results with vertical, use_case,
                           modules, and confidence score.
        """
        # Truncate prompt to avoid token limits
        truncated_prompt = prompt[:4000]
        
        system_message = """You are an AI assistant that classifies app development requests.
Analyze the user's request and determine:
1. The industry vertical (e.g., logistics, hr, healthcare, retail, general)
2. The specific use case
3. Recommended modules (e.g., time_tracking, gps, forms, inventory, etc.)
4. Your confidence score (0.0 to 1.0)

Respond ONLY with valid JSON in this format:
{
    "vertical": "industry_name",
    "use_case": "specific_use_case_description",
    "modules": ["module1", "module2"],
    "confidence": 0.95
}"""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": truncated_prompt},
        ]
        
        response = await self._make_request(
            model=self.INTENT_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
        )
        
        if not response:
            logger.error("Intent classification failed")
            return None
        
        import json
        try:
            result = json.loads(response)
            logger.info(
                "Intent classified",
                vertical=result.get("vertical"),
                confidence=result.get("confidence"),
            )
            return result
        except json.JSONDecodeError as e:
            logger.error("Failed to parse intent response", error=str(e))
            return None
    
    async def generate_config(self, intent: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate JSON configuration from classified intent.
        
        Uses GPT-OSS-20b for structured JSON output.
        
        Args:
            intent: Classified intent from classify_intent().
            
        Returns:
            Optional[Dict]: Generated configuration schema.
        """
        system_message = """You are an AI assistant that generates app configuration schemas.
Based on the intent analysis, create a detailed JSON configuration for a React PWA.

Include:
1. App name and description
2. UI components needed
3. Data models
4. Required modules
5. Offline sync requirements

Respond ONLY with valid JSON in this format:
{
    "name": "app_name",
    "description": "app_description",
    "modules": ["module1", "module2"],
    "components": ["Component1", "Component2"],
    "data_models": {
        "ModelName": {
            "field1": "type",
            "field2": "type"
        }
    },
    "offline_sync": true
}"""
        
        intent_text = f"""Vertical: {intent.get('vertical', 'general')}
Use Case: {intent.get('use_case', 'General purpose app')}
Modules: {', '.join(intent.get('modules', []))}"""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": intent_text},
        ]
        
        response = await self._make_request(
            model=self.CONFIG_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
        )
        
        if not response:
            logger.error("Config generation failed")
            return None
        
        import json
        try:
            config = json.loads(response)
            logger.info(
                "Config generated",
                app_name=config.get("name"),
                modules=len(config.get("modules", [])),
            )
            return config
        except json.JSONDecodeError as e:
            logger.error("Failed to parse config response", error=str(e))
            return None
    
    async def generate_code(
        self,
        config: Dict[str, Any],
        complexity: str = "simple",
    ) -> Optional[Dict[str, Any]]:
        """
        Generate React/PWA code from configuration.
        
        Routes to appropriate model based on complexity:
        - simple: GPT-OSS-20b
        - complex: Llama-3.3-70b-versatile
        
        Args:
            config: Configuration schema from generate_config().
            complexity: App complexity level ("simple" or "complex").
            
        Returns:
            Optional[Dict]: Generated code files and service worker.
        """
        model = (
            self.COMPLEX_CODE_MODEL
            if complexity == "complex"
            else self.SIMPLE_CODE_MODEL
        )
        
        system_message = """You are an expert React developer. Generate a complete PWA application.

Requirements:
1. Create index.html with React root div and Tailwind CSS CDN
2. Create App.tsx with functional components based on the config
3. Create service-worker.js for offline caching
4. Use TypeScript interfaces
5. Include proper error handling
6. Make it mobile-responsive

Return a JSON object with file contents:
{
    "files": {
        "index.html": "<!DOCTYPE html>...",
        "App.tsx": "import React...",
        "main.tsx": "import React..."
    },
    "service_worker": "// Service worker code..."
}"""
        
        config_text = f"""Generate a PWA with these specifications:
Name: {config.get('name', 'Wesza App')}
Description: {config.get('description', 'Generated app')}
Modules: {', '.join(config.get('modules', []))}
Components: {', '.join(config.get('components', []))}
Data Models: {config.get('data_models', {})}
Offline Sync: {config.get('offline_sync', True)}"""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": config_text},
        ]
        
        response = await self._make_request(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
        )
        
        if not response:
            logger.error("Code generation failed", complexity=complexity)
            return None
        
        import json
        try:
            code_files = json.loads(response)
            logger.info(
                "Code generated",
                complexity=complexity,
                files=len(code_files.get("files", {})),
            )
            return code_files
        except json.JSONDecodeError as e:
            logger.error("Failed to parse code response", error=str(e))
            return None
