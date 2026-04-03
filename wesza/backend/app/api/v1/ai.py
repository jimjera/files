"""
AI orchestration API endpoints.

This module provides endpoints for AI-powered app generation,
including intent classification, template generation, and code generation.
"""

import structlog
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.ai import (
    PromptRequest,
    TemplateResponse,
    CodeGenerationResponse,
)
from app.middleware.auth import get_current_user
from app.services.ai_orchestrator import AIOrchestrator
from app.services.app_generator import AppGenerator
from app.services.deployer import Deployer

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/prompt",
    response_model=CodeGenerationResponse,
    summary="Generate app from prompt",
    description="Process a natural language prompt to generate a complete PWA.",
)
async def generate_app_from_prompt(
    request: PromptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a complete PWA from a natural language prompt.
    
    This endpoint orchestrates the full AI pipeline:
    1. Classify user intent
    2. Generate JSON template
    3. Generate React/PWA code
    4. Deploy to CDN
    
    Args:
        request: Prompt request with natural language description.
        current_user: Authenticated user.
        db: Database session.
        
    Returns:
        CodeGenerationResponse: Generated app files and deployment URL.
        
    Raises:
        HTTPException: If AI processing fails.
    """
    start_time = time.time()
    
    try:
        # Initialize services
        orchestrator = AIOrchestrator()
        generator = AppGenerator()
        deployer = Deployer()
        
        # Step 1: Classify intent
        logger.info("Classifying intent", user_id=str(current_user.id))
        intent = await orchestrator.classify_intent(request.prompt)
        
        if not intent or "vertical" not in intent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to classify intent",
            )
        
        # Step 2: Generate config
        logger.info("Generating config", vertical=intent.get("vertical"))
        config = await orchestrator.generate_config(intent)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to generate configuration",
            )
        
        # Step 3: Generate code
        complexity = "complex" if len(config.get("modules", [])) > 3 else "simple"
        logger.info("Generating code", complexity=complexity)
        code_files = await orchestrator.generate_code(config, complexity)
        
        if not code_files or "files" not in code_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to generate code",
            )
        
        # Step 4: Deploy to Spaces
        logger.info("Deploying app", user_id=str(current_user.id))
        deploy_url = await deployer.upload_to_spaces(
            user_id=str(current_user.id),
            files=code_files["files"],
        )
        
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "App generated successfully",
            user_id=str(current_user.id),
            deploy_url=deploy_url,
            generation_time_ms=generation_time_ms,
        )
        
        return CodeGenerationResponse(
            files=code_files["files"],
            service_worker=code_files.get("service_worker"),
            deploy_url=deploy_url,
            generation_time_ms=generation_time_ms,
        )
    
    except Exception as e:
        logger.error(
            "App generation failed",
            user_id=str(current_user.id),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"App generation failed: {str(e)}",
        )


@router.post(
    "/classify",
    response_model=TemplateResponse,
    summary="Classify intent",
    description="Classify a prompt to detect vertical and use case.",
)
async def classify_intent(
    request: PromptRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Classify user intent from prompt.
    
    Args:
        request: Prompt request.
        current_user: Authenticated user.
        
    Returns:
        TemplateResponse: Classification results.
    """
    try:
        orchestrator = AIOrchestrator()
        intent = await orchestrator.classify_intent(request.prompt)
        
        if not intent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to classify intent",
            )
        
        return TemplateResponse(
            vertical=intent.get("vertical", "general"),
            config_json=intent.get("config", {}),
            confidence=intent.get("confidence", 0.0),
            message="Intent classified successfully",
        )
    
    except Exception as e:
        logger.error("Intent classification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}",
        )
