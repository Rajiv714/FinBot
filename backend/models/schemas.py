"""
Data models and schemas for FinBot API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# Chatbot Schemas

class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for chatbot query"""
    query: str = Field(..., description="User's question")
    include_context: bool = Field(default=True, description="Whether to use RAG context")
    top_k: Optional[int] = Field(default=None, description="Number of documents to retrieve")
    score_threshold: Optional[float] = Field(default=None, description="Minimum similarity score")


class ChatHistoryRequest(BaseModel):
    """Request for chat with conversation history"""
    messages: List[ChatMessage] = Field(..., description="Conversation history")
    include_context: bool = Field(default=True, description="Whether to use RAG context")
    top_k: Optional[int] = Field(default=None, description="Number of documents to retrieve")
    score_threshold: Optional[float] = Field(default=None, description="Minimum similarity score")


class Source(BaseModel):
    """Document source information"""
    text: str = Field(..., description="Text excerpt")
    score: float = Field(..., description="Relevance score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class ChatResponse(BaseModel):
    """Response from chatbot"""
    answer: str = Field(..., description="Generated answer")
    sources: List[Source] = Field(default_factory=list, description="Retrieved sources")
    context_used: bool = Field(..., description="Whether context was used")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


# Handout Schemas

class HandoutRequest(BaseModel):
    """Request for handout generation"""
    topic: str = Field(..., description="Topic for the handout")
    target_length: int = Field(default=1200, description="Target word count (1000-1200)")
    include_google_search: bool = Field(default=True, description="Include Google search results")
    search_depth: str = Field(default="standard", description="Search depth: basic, standard, comprehensive")


class AgentOutput(BaseModel):
    """Output from a single agent"""
    agent_name: str = Field(..., description="Name of the agent")
    execution_time: float = Field(..., description="Execution time in seconds")
    word_count: int = Field(default=0, description="Word count of output")
    success: bool = Field(..., description="Whether execution was successful")
    data: Dict[str, Any] = Field(default_factory=dict, description="Agent output data")


class HandoutResponse(BaseModel):
    """Response from handout generation"""
    topic: str = Field(..., description="Handout topic")
    handout_content: str = Field(..., description="Generated handout content")
    word_count: int = Field(..., description="Total word count")
    filepath: Optional[str] = Field(default=None, description="Saved file path")
    agent_outputs: List[AgentOutput] = Field(default_factory=list, description="Individual agent outputs")
    total_execution_time: float = Field(..., description="Total generation time")
    timestamp: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    success: bool = Field(..., description="Whether generation was successful")


# Ingestion Schemas

class IngestionRequest(BaseModel):
    """Request for document ingestion"""
    data_folder: str = Field(default="Data", description="Folder containing PDF files")
    clear_existing: bool = Field(default=False, description="Whether to clear existing data")
    file_paths: Optional[List[str]] = Field(default=None, description="Specific files to ingest")


class IngestionProgress(BaseModel):
    """Progress update during ingestion"""
    current_file: str = Field(..., description="Currently processing file")
    files_processed: int = Field(..., description="Number of files processed")
    total_files: int = Field(..., description="Total files to process")
    chunks_created: int = Field(default=0, description="Number of chunks created")
    status: str = Field(..., description="Current status")


class IngestionResponse(BaseModel):
    """Response from document ingestion"""
    success: bool = Field(..., description="Whether ingestion succeeded")
    files_processed: int = Field(..., description="Number of files processed")
    total_chunks: int = Field(..., description="Total chunks created")
    execution_time: float = Field(..., description="Total execution time")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    timestamp: datetime = Field(default_factory=datetime.now, description="Ingestion timestamp")


# System Schemas

class SystemStatus(BaseModel):
    """System health and status"""
    status: str = Field(..., description="Overall system status: healthy, degraded, error")
    vector_db_healthy: bool = Field(..., description="Vector database health")
    vector_db_documents: int = Field(default=0, description="Number of documents in vector DB")
    llm_configured: bool = Field(..., description="Whether LLM is configured")
    embedding_model: str = Field(..., description="Embedding model name")
    components: Dict[str, Any] = Field(default_factory=dict, description="Component details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Status check timestamp")


class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


# ============================================================================
# Document Summariser Schemas
# ============================================================================

class SummariserRequest(BaseModel):
    """Request for document summarisation"""
    user_query: Optional[str] = Field(default=None, description="Optional user query about the document")


class SummariserResponse(BaseModel):
    """Response from document summarisation"""
    success: bool = Field(..., description="Whether summarisation was successful")
    document_type: Optional[str] = Field(default=None, description="Type of document detected")
    analysis: Optional[str] = Field(default=None, description="AI analysis of the document")
    text_length: Optional[int] = Field(default=None, description="Length of processed text")
    filename: Optional[str] = Field(default=None, description="Name of the analyzed file")
    error: Optional[str] = Field(default=None, description="Error message if failed")

