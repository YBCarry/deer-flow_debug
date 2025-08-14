# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Main interaction logger for DeerFlow.

This module provides the core functionality for logging all interactions,
agent activities, workflow events, and tool usage in the DeerFlow system.
"""

import json
import logging
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path

from langchain_core.messages import BaseMessage


@dataclass
class InteractionEvent:
    """Represents a single interaction event."""
    event_id: str
    session_id: str
    timestamp: str
    event_type: str
    user_input: Optional[str] = None
    agent_response: Optional[str] = None
    agent_name: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[str] = None
    duration_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class WorkflowEvent:
    """Represents a workflow event."""
    event_id: str
    session_id: str
    timestamp: str
    workflow_type: str
    node_name: str
    status: str  # started, completed, error
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


@dataclass
class AgentActivity:
    """Represents an agent activity."""
    event_id: str
    session_id: str  
    timestamp: str
    agent_name: str
    activity_type: str
    llm_model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    duration_ms: Optional[float] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass 
class ToolUsage:
    """Represents tool usage."""
    event_id: str
    session_id: str
    timestamp: str
    tool_name: str
    agent_name: Optional[str] = None
    input_parameters: Optional[Dict[str, Any]] = None
    output_result: Optional[str] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


class InteractionLogger:
    """Main logger for DeerFlow interactions."""
    
    def __init__(self, session_id: Optional[str] = None):
        """Initialize the interaction logger."""
        self.session_id = session_id or str(uuid.uuid4())
        
        # Get specialized loggers
        self.interaction_logger = logging.getLogger("deer_flow.interactions")
        self.agent_logger = logging.getLogger("deer_flow.agents")
        self.workflow_logger = logging.getLogger("deer_flow.workflows") 
        self.tool_logger = logging.getLogger("deer_flow.tools")
        self.performance_logger = logging.getLogger("deer_flow.performance")
        self.security_logger = logging.getLogger("deer_flow.security")
    
    def log_interaction(
        self,
        event_type: str,
        user_input: Optional[str] = None,
        agent_response: Optional[str] = None,
        agent_name: Optional[str] = None,
        duration_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> str:
        """Log a user-agent interaction."""
        event_id = str(uuid.uuid4())
        event = InteractionEvent(
            event_id=event_id,
            session_id=self.session_id,
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            user_input=user_input,
            agent_response=agent_response,
            agent_name=agent_name,
            duration_ms=duration_ms,
            metadata=metadata or {},
            error=error,
        )
        
        # Create log record with custom attributes
        record = logging.LogRecord(
            name="deer_flow.interactions",
            level=logging.INFO,
            pathname="", lineno=0, msg="",
            args=(), exc_info=None
        )
        
        record.session_id = self.session_id
        record.interaction_type = event_type
        record.interaction_data = asdict(event)
        record.duration = duration_ms
        record.agent_name = agent_name
        
        self.interaction_logger.handle(record)
        return event_id
    
    def log_agent_activity(
        self,
        agent_name: str,
        activity_type: str,
        llm_model: Optional[str] = None,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        duration_ms: Optional[float] = None,
        input_data: Optional[str] = None,
        output_data: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Log agent activity."""
        event_id = str(uuid.uuid4())
        activity = AgentActivity(
            event_id=event_id,
            session_id=self.session_id,
            timestamp=datetime.now().isoformat(),
            agent_name=agent_name,
            activity_type=activity_type,
            llm_model=llm_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=(prompt_tokens or 0) + (completion_tokens or 0) if prompt_tokens and completion_tokens else None,
            duration_ms=duration_ms,
            input_data=input_data,
            output_data=output_data,
            metadata=metadata or {},
        )
        
        # Create log record
        record = logging.LogRecord(
            name="deer_flow.agents",
            level=logging.INFO,
            pathname="", lineno=0, msg=f"Agent {agent_name} performed {activity_type}",
            args=(), exc_info=None
        )
        
        record.session_id = self.session_id
        record.agent_name = agent_name
        record.action = activity_type
        record.agent_data = asdict(activity)
        record.llm_model = llm_model
        record.tokens_used = (prompt_tokens or 0) + (completion_tokens or 0) if prompt_tokens and completion_tokens else None
        
        self.agent_logger.handle(record)
        return event_id
    
    def log_workflow_event(
        self,
        workflow_type: str,
        node_name: str,
        status: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
        error: Optional[str] = None,
    ) -> str:
        """Log workflow event."""
        event_id = str(uuid.uuid4())
        event = WorkflowEvent(
            event_id=event_id,
            session_id=self.session_id,
            timestamp=datetime.now().isoformat(),
            workflow_type=workflow_type,
            node_name=node_name,
            status=status,
            input_data=input_data,
            output_data=output_data,
            duration_ms=duration_ms,
            error=error,
        )
        
        level = logging.ERROR if status == "error" else logging.INFO
        message = f"Workflow {workflow_type}.{node_name}: {status}"
        if error:
            message += f" - {error}"
        
        self.workflow_logger.log(level, message, extra={
            "session_id": self.session_id,
            "workflow_event": asdict(event)
        })
        
        return event_id
    
    def log_tool_usage(
        self,
        tool_name: str,
        input_parameters: Optional[Dict[str, Any]] = None,
        output_result: Optional[str] = None,
        agent_name: Optional[str] = None,
        duration_ms: Optional[float] = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> str:
        """Log tool usage."""
        event_id = str(uuid.uuid4())
        usage = ToolUsage(
            event_id=event_id,
            session_id=self.session_id,
            timestamp=datetime.now().isoformat(),
            tool_name=tool_name,
            agent_name=agent_name,
            input_parameters=input_parameters,
            output_result=output_result,
            duration_ms=duration_ms,
            success=success,
            error=error,
        )
        
        level = logging.ERROR if not success else logging.INFO
        message = f"Tool {tool_name} used by {agent_name or 'unknown'}"
        if error:
            message += f" - Error: {error}"
        
        # Create log record
        record = logging.LogRecord(
            name="deer_flow.tools",
            level=level,
            pathname="", lineno=0, msg=message,
            args=(), exc_info=None
        )
        
        record.session_id = self.session_id
        record.tool_name = tool_name
        record.agent_name = agent_name
        record.tool_data = asdict(usage)
        
        self.tool_logger.handle(record)
        return event_id
    
    def log_performance_metric(
        self,
        metric_name: str,
        value: Union[float, int],
        unit: str = "ms",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log performance metrics."""
        self.performance_logger.info(
            f"Performance metric {metric_name}: {value}{unit}",
            extra={
                "session_id": self.session_id,
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "metadata": metadata or {},
            }
        )
    
    def log_security_event(
        self,
        event_type: str,
        description: str,
        severity: str = "INFO",
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log security events."""
        level = getattr(logging, severity.upper(), logging.INFO)
        self.security_logger.log(
            level,
            f"Security event {event_type}: {description}",
            extra={
                "session_id": self.session_id,
                "event_type": event_type,
                "user_id": user_id,
                "ip_address": ip_address,
                "metadata": metadata or {},
            }
        )
    
    @contextmanager
    def timing(self, operation_name: str):
        """Context manager for timing operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = (time.time() - start_time) * 1000
            self.log_performance_metric(operation_name, duration, "ms")


# Global logger instance
_global_logger: Optional[InteractionLogger] = None


def get_interaction_logger(session_id: Optional[str] = None) -> InteractionLogger:
    """Get or create the global interaction logger."""
    global _global_logger
    if _global_logger is None or (session_id and _global_logger.session_id != session_id):
        _global_logger = InteractionLogger(session_id)
    return _global_logger


def log_interaction(
    event_type: str,
    user_input: Optional[str] = None,
    agent_response: Optional[str] = None,
    agent_name: Optional[str] = None,
    duration_ms: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """Convenience function to log interactions."""
    logger = get_interaction_logger(session_id)
    return logger.log_interaction(
        event_type=event_type,
        user_input=user_input,
        agent_response=agent_response,
        agent_name=agent_name,
        duration_ms=duration_ms,
        metadata=metadata,
        error=error,
    )


def log_agent_activity(
    agent_name: str,
    activity_type: str,
    llm_model: Optional[str] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    duration_ms: Optional[float] = None,
    input_data: Optional[str] = None,
    output_data: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
) -> str:
    """Convenience function to log agent activities."""
    logger = get_interaction_logger(session_id)
    return logger.log_agent_activity(
        agent_name=agent_name,
        activity_type=activity_type,
        llm_model=llm_model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        duration_ms=duration_ms,
        input_data=input_data,
        output_data=output_data,
        metadata=metadata,
    )


def log_workflow_event(
    workflow_type: str,
    node_name: str,
    status: str,
    input_data: Optional[Dict[str, Any]] = None,
    output_data: Optional[Dict[str, Any]] = None,
    duration_ms: Optional[float] = None,
    error: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """Convenience function to log workflow events."""
    logger = get_interaction_logger(session_id)
    return logger.log_workflow_event(
        workflow_type=workflow_type,
        node_name=node_name,
        status=status,
        input_data=input_data,
        output_data=output_data,
        duration_ms=duration_ms,
        error=error,
    )


def log_tool_usage(
    tool_name: str,
    input_parameters: Optional[Dict[str, Any]] = None,
    output_result: Optional[str] = None,
    agent_name: Optional[str] = None,
    duration_ms: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """Convenience function to log tool usage."""
    logger = get_interaction_logger(session_id)
    return logger.log_tool_usage(
        tool_name=tool_name,
        input_parameters=input_parameters,
        output_result=output_result,
        agent_name=agent_name,
        duration_ms=duration_ms,
        success=success,
        error=error,
    )


def logged_interaction(func: Callable) -> Callable:
    """Decorator to automatically log function interactions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        function_name = f"{func.__module__}.{func.__name__}"
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            log_interaction(
                event_type="function_call",
                agent_name=function_name,
                duration_ms=duration_ms,
                metadata={
                    "function": function_name,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                }
            )
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_interaction(
                event_type="function_error",
                agent_name=function_name,
                duration_ms=duration_ms,
                error=str(e),
                metadata={
                    "function": function_name,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                }
            )
            raise
            
    return wrapper


def logged_agent_activity(agent_name: str, activity_type: str):
    """Decorator to automatically log agent activities."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                log_agent_activity(
                    agent_name=agent_name,
                    activity_type=activity_type,
                    duration_ms=duration_ms,
                    metadata={
                        "function": f"{func.__module__}.{func.__name__}",
                        "success": True,
                    }
                )
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                log_agent_activity(
                    agent_name=agent_name,
                    activity_type=f"{activity_type}_error",
                    duration_ms=duration_ms,
                    metadata={
                        "function": f"{func.__module__}.{func.__name__}",
                        "error": str(e),
                        "success": False,
                    }
                )
                raise
                
        return wrapper
    return decorator