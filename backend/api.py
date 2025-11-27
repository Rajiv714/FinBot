"""
FastAPI Backend for FinBot
Provides REST API endpoints for chatbot, handout generation, and document ingestion
"""
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any
import uvicorn

# Add parent directory to path
parent_path = str(Path(__file__).parent.parent)
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

from backend.models.schemas import (
    ChatRequest,
    ChatHistoryRequest,
    ChatResponse,
    HandoutRequest,
    HandoutResponse,
    IngestionRequest,
    IngestionResponse,
    SystemStatus,
    ErrorResponse
)
from backend.services import (
    get_chatbot_service,
    get_handout_service,
    get_ingestion_service
)

# ============================================================================
# FastAPI App Configuration
# ============================================================================

app = FastAPI(
    title="FinBot API",
    description="REST API for Financial Literacy Chatbot and Educational Content Generation",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Chatbot Endpoints
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse, tags=["Chatbot"])
async def chat_query(request: ChatRequest) -> ChatResponse:
    """
    Process a single user query using RAG.
    
    Args:
        request: ChatRequest with query and optional parameters
        
    Returns:
        ChatResponse with answer and sources
    """
    try:
        chatbot = get_chatbot_service()
        
        result = chatbot.chat_query(
            query=request.query,
            include_context=request.include_context,
            top_k=request.top_k,
            score_threshold=request.score_threshold
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
        
        return ChatResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            context_used=result.get("context_used", False)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/history", response_model=ChatResponse, tags=["Chatbot"])
async def chat_with_history(request: ChatHistoryRequest) -> ChatResponse:
    """
    Process chat with conversation history using RAG.
    
    Args:
        request: ChatHistoryRequest with messages and optional parameters
        
    Returns:
        ChatResponse with answer and sources
    """
    try:
        chatbot = get_chatbot_service()
        
        # Convert Pydantic models to dicts
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        result = chatbot.chat_with_history(
            messages=messages,
            include_context=request.include_context,
            top_k=request.top_k,
            score_threshold=request.score_threshold
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
        
        return ChatResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            context_used=result.get("context_used", False)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Handout Generation Endpoints
# ============================================================================

@app.post("/api/handouts", response_model=HandoutResponse, tags=["Handout Generation"])
async def create_handout(request: HandoutRequest) -> HandoutResponse:
    """
    Generate educational handout on a financial topic.
    
    Uses 3-agent pipeline:
    - ContentExtractor: Extracts from vector DB
    - GoogleSearch: Gets latest news (optional)
    - HandoutGenerator: Creates 1000-1200 word handout
    
    Args:
        request: HandoutRequest with topic and parameters
        
    Returns:
        HandoutResponse with generated content
    """
    try:
        handout_service = get_handout_service()
        
        result = handout_service.create_handout(
            topic=request.topic,
            target_length=request.target_length,
            include_google_search=request.include_google_search,
            search_depth=request.search_depth
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
        
        return HandoutResponse(
            topic=result["topic"],
            handout_content=result["handout_content"],
            word_count=result["word_count"],
            filepath=result.get("filepath"),
            agent_outputs=result.get("agent_outputs", []),
            total_execution_time=result["total_execution_time"],
            success=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Document Ingestion Endpoints
# ============================================================================

@app.post("/api/ingest", response_model=IngestionResponse, tags=["Document Ingestion"])
async def ingest_documents(request: IngestionRequest, background_tasks: BackgroundTasks):
    """
    Ingest PDF documents into the vector database.
    
    Args:
        request: IngestionRequest with data folder and parameters
        background_tasks: FastAPI background tasks
        
    Returns:
        IngestionResponse with ingestion results
    """
    try:
        ingestion_service = get_ingestion_service()
        
        result = ingestion_service.ingest_documents(
            data_folder=request.data_folder,
            clear_existing=request.clear_existing,
            file_paths=request.file_paths
        )
        
        return IngestionResponse(
            success=result["success"],
            files_processed=result["files_processed"],
            total_chunks=result["total_chunks"],
            execution_time=result["execution_time"],
            errors=result.get("errors", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# System Status Endpoints
# ============================================================================

@app.get("/api/status", response_model=SystemStatus, tags=["System"])
async def get_system_status() -> SystemStatus:
    """
    Get system health and status.
    
    Returns:
        SystemStatus with component health information
    """
    try:
        chatbot = get_chatbot_service()
        status = chatbot.get_status()
        
        return SystemStatus(
            status=status["status"],
            vector_db_healthy=status["vector_db_healthy"],
            vector_db_documents=status["vector_db_documents"],
            llm_configured=status["llm_configured"],
            embedding_model=status["embedding_model"],
            components=status.get("components", {})
        )
        
    except Exception as e:
        return SystemStatus(
            status="error",
            vector_db_healthy=False,
            vector_db_documents=0,
            llm_configured=False,
            embedding_model="unknown",
            components={"error": str(e)}
        )


@app.get("/api/health", tags=["System"])
async def health_check() -> Dict[str, str]:
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "FinBot API"}


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "FinBot API",
        "version": "1.0.0",
        "description": "REST API for Financial Literacy Chatbot",
        "endpoints": {
            "chatbot": {
                "chat": "/api/chat",
                "chat_history": "/api/chat/history"
            },
            "handouts": {
                "create": "/api/handouts"
            },
            "ingestion": {
                "ingest": "/api/ingest"
            },
            "system": {
                "status": "/api/status",
                "health": "/api/health"
            }
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
