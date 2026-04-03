"""
AI orchestration API endpoints.
"""

import structlog
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.app import App
from app.schemas.ai import (
    PromptRequest,
    TemplateResponse,
    CodeGenerationResponse,
    GenerateRequest,
)
from app.middleware.auth import get_current_user
from app.services.ai_orchestrator import AIOrchestrator
from app.services.app_generator import AppGenerator
from app.services.deployer import Deployer

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/generate",
    response_model=dict,
    summary="Generate AI response for app",
    description="Generate an AI response using a specific app's configuration.",
)
async def generate_response_endpoint(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate an AI response using the app's template and configuration."""
    import uuid
    
    try:
        app_uuid = uuid.UUID(request.app_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid app ID format",
        )
    
    result = await db.execute(select(App).where(App.id == app_uuid))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found",
        )
    
    if app.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this app",
        )
    
    try:
        orchestrator = AIOrchestrator()
        response = await orchestrator.generate_response(
            app_config=app.config_json,
            user_input=request.user_input,
        )
        
        return {
            "response": response,
            "app_id": str(app.id),
        }
    
    except Exception as e:
        logger.error("AI generation failed", app_id=str(app.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {str(e)}",
        )


@router.post("/prompt", response_model=CodeGenerationResponse)
async def generate_app_from_prompt(
    request: PromptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a complete PWA from a natural language prompt."""
    start_time = time.time()
    
    try:
        orchestrator = AIOrchestrator()
        generator = AppGenerator()
        deployer = Deployer()
        
        intent = await orchestrator.classify_intent(request.prompt)
        if not intent or "vertical" not in intent:
            raise HTTPException(status_code=400, detail="Failed to classify intent")
        
        config = await orchestrator.generate_config(intent)
        if not config:
            raise HTTPException(status_code=400, detail="Failed to generate configuration")
        
        complexity = "complex" if len(config.get("modules", [])) > 3 else "simple"
        code_files = await orchestrator.generate_code(config, complexity)
        
        if not code_files or "files" not in code_files:
            raise HTTPException(status_code=400, detail="Failed to generate code")
        
        deploy_url = await deployer.upload_to_spaces(
            user_id=str(current_user.id),
            files=code_files["files"],
        )
        
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        return CodeGenerationResponse(
            files=code_files["files"],
            service_worker=code_files.get("service_worker"),
            deploy_url=deploy_url,
            generation_time_ms=generation_time_ms,
        )
    
    except Exception as e:
        logger.error("App generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"App generation failed: {str(e)}")


@router.post("/classify", response_model=TemplateResponse)
async def classify_intent_endpoint(
    request: PromptRequest,
    current_user: User = Depends(get_current_user),
):
    """Classify user intent from prompt."""
    try:
        orchestrator = AIOrchestrator()
        intent = await orchestrator.classify_intent(request.prompt)
        
        if not intent:
            raise HTTPException(status_code=400, detail="Failed to classify intent")
        
        return TemplateResponse(
            vertical=intent.get("vertical", "general"),
            config_json=intent.get("config", {}),
            confidence=intent.get("confidence", 0.0),
            message="Intent classified successfully",
        )
    
    except Exception as e:
        logger.error("Intent classification failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
