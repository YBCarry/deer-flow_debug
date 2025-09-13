# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PromptFileInfo(BaseModel):
    """Prompt file information"""
    filename: str = Field(..., description="Name of the prompt file")
    size: int = Field(..., description="File size in bytes")
    last_modified: datetime = Field(..., description="Last modification time")
    content_preview: Optional[str] = Field(None, description="Preview of file content (first 200 chars)")


class PromptUploadRequest(BaseModel):
    """Request for uploading prompt files"""
    filename: str = Field(..., description="Name of the file to upload")
    content: str = Field(..., description="Content of the file")


class PromptUploadResponse(BaseModel):
    """Response for prompt file upload"""
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Success or error message")
    filename: str = Field(..., description="Name of the uploaded file")


class PromptListResponse(BaseModel):
    """Response for listing prompt files"""
    files: List[PromptFileInfo] = Field(..., description="List of prompt files")
    allowed_files: List[str] = Field(..., description="List of allowed prompt filenames")