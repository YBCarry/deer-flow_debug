# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Custom formatters for DeerFlow logging.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """A formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as structured JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any custom fields from the record
        for key, value in record.__dict__.items():
            if key not in {
                "name", "levelname", "levelno", "pathname", "filename", 
                "module", "exc_info", "exc_text", "stack_info", "lineno", 
                "funcName", "created", "msecs", "relativeCreated", "thread", 
                "threadName", "processName", "process", "getMessage", "msg", "args"
            }:
                log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False)


class InteractionFormatter(logging.Formatter):
    """A formatter specifically for interaction logs with enhanced readability."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record for interaction logs."""
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        
        # Base log structure
        log_data = {
            "timestamp": timestamp,
            "session_id": getattr(record, "session_id", "unknown"),
            "interaction_type": getattr(record, "interaction_type", "general"),
            "user_id": getattr(record, "user_id", "anonymous"),
            "message": record.getMessage(),
        }
        
        # Add specific interaction data
        if hasattr(record, "interaction_data"):
            log_data.update(record.interaction_data)
        
        # Add performance metrics if available
        if hasattr(record, "duration"):
            log_data["duration_ms"] = record.duration
        
        # Add agent information if available
        if hasattr(record, "agent_name"):
            log_data["agent"] = record.agent_name
        
        # Add tool information if available  
        if hasattr(record, "tool_name"):
            log_data["tool"] = record.tool_name
        
        return json.dumps(log_data, ensure_ascii=False, indent=2)


class AgentFormatter(logging.Formatter):
    """A formatter specifically for agent activity logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record for agent logs."""
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        
        log_data = {
            "timestamp": timestamp,
            "agent": getattr(record, "agent_name", "unknown"),
            "action": getattr(record, "action", "activity"),
            "session_id": getattr(record, "session_id", "unknown"),
            "message": record.getMessage(),
        }
        
        # Add agent-specific data
        if hasattr(record, "agent_data"):
            log_data.update(record.agent_data)
        
        # Add LLM information
        if hasattr(record, "llm_model"):
            log_data["llm_model"] = record.llm_model
        
        # Add token usage if available
        if hasattr(record, "tokens_used"):
            log_data["tokens_used"] = record.tokens_used
        
        return json.dumps(log_data, ensure_ascii=False)