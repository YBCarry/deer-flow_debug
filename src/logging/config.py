# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Logging configuration and setup for DeerFlow.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .handlers import DateRotatingFileHandler
from .formatters import StructuredFormatter, InteractionFormatter


@dataclass
class LoggingConfig:
    """Configuration for DeerFlow logging system."""
    
    # Base logging directory
    log_dir: str = "logs"
    
    # Interaction logging
    enable_interaction_logging: bool = True
    interaction_log_level: str = "INFO"
    
    # Agent activity logging
    enable_agent_logging: bool = True
    agent_log_level: str = "INFO"
    
    # Workflow event logging
    enable_workflow_logging: bool = True
    workflow_log_level: str = "INFO"
    
    # Tool usage logging
    enable_tool_logging: bool = True
    tool_log_level: str = "INFO"
    
    # System logging
    system_log_level: str = "INFO"
    
    # Log rotation
    max_log_files: int = 30  # Keep logs for 30 days
    
    # Performance logging
    enable_performance_logging: bool = True
    
    # Security logging
    enable_security_logging: bool = True
    
    @classmethod
    def from_env(cls) -> "LoggingConfig":
        """Create logging config from environment variables."""
        return cls(
            log_dir=os.getenv("DEER_FLOW_LOG_DIR", "logs"),
            enable_interaction_logging=os.getenv("DEER_FLOW_LOG_INTERACTIONS", "true").lower() == "true",
            interaction_log_level=os.getenv("DEER_FLOW_INTERACTION_LOG_LEVEL", "INFO"),
            enable_agent_logging=os.getenv("DEER_FLOW_LOG_AGENTS", "true").lower() == "true",
            agent_log_level=os.getenv("DEER_FLOW_AGENT_LOG_LEVEL", "INFO"),
            enable_workflow_logging=os.getenv("DEER_FLOW_LOG_WORKFLOWS", "true").lower() == "true",
            workflow_log_level=os.getenv("DEER_FLOW_WORKFLOW_LOG_LEVEL", "INFO"),
            enable_tool_logging=os.getenv("DEER_FLOW_LOG_TOOLS", "true").lower() == "true",
            tool_log_level=os.getenv("DEER_FLOW_TOOL_LOG_LEVEL", "INFO"),
            system_log_level=os.getenv("DEER_FLOW_SYSTEM_LOG_LEVEL", "INFO"),
            max_log_files=int(os.getenv("DEER_FLOW_MAX_LOG_FILES", "30")),
            enable_performance_logging=os.getenv("DEER_FLOW_LOG_PERFORMANCE", "true").lower() == "true",
            enable_security_logging=os.getenv("DEER_FLOW_LOG_SECURITY", "true").lower() == "true",
        )


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """Set up comprehensive logging for DeerFlow."""
    if config is None:
        config = LoggingConfig.from_env()
    
    # Create log directory
    log_dir = Path(config.log_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (log_dir / "interactions").mkdir(exist_ok=True)
    (log_dir / "agents").mkdir(exist_ok=True)
    (log_dir / "workflows").mkdir(exist_ok=True)
    (log_dir / "tools").mkdir(exist_ok=True)
    (log_dir / "system").mkdir(exist_ok=True)
    (log_dir / "performance").mkdir(exist_ok=True)
    (log_dir / "security").mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.system_log_level))
    
    # Remove existing handlers to avoid duplication
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # System log handler
    system_handler = DateRotatingFileHandler(
        log_dir / "system" / "system.log",
        max_files=config.max_log_files
    )
    system_handler.setFormatter(StructuredFormatter())
    system_handler.setLevel(getattr(logging, config.system_log_level))
    root_logger.addHandler(system_handler)
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    _setup_interaction_logger(config)
    _setup_agent_logger(config)
    _setup_workflow_logger(config)
    _setup_tool_logger(config)
    _setup_performance_logger(config)
    _setup_security_logger(config)


def _setup_interaction_logger(config: LoggingConfig) -> None:
    """Set up interaction logger."""
    if not config.enable_interaction_logging:
        return
        
    logger = logging.getLogger("deer_flow.interactions")
    logger.setLevel(getattr(logging, config.interaction_log_level))
    logger.propagate = False
    
    handler = DateRotatingFileHandler(
        Path(config.log_dir) / "interactions" / "interactions.log",
        max_files=config.max_log_files
    )
    handler.setFormatter(InteractionFormatter())
    logger.addHandler(handler)


def _setup_agent_logger(config: LoggingConfig) -> None:
    """Set up agent logger."""
    if not config.enable_agent_logging:
        return
        
    logger = logging.getLogger("deer_flow.agents")
    logger.setLevel(getattr(logging, config.agent_log_level))
    logger.propagate = False
    
    handler = DateRotatingFileHandler(
        Path(config.log_dir) / "agents" / "agents.log",
        max_files=config.max_log_files
    )
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)


def _setup_workflow_logger(config: LoggingConfig) -> None:
    """Set up workflow logger.""" 
    if not config.enable_workflow_logging:
        return
        
    logger = logging.getLogger("deer_flow.workflows")
    logger.setLevel(getattr(logging, config.workflow_log_level))
    logger.propagate = False
    
    handler = DateRotatingFileHandler(
        Path(config.log_dir) / "workflows" / "workflows.log",
        max_files=config.max_log_files
    )
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)


def _setup_tool_logger(config: LoggingConfig) -> None:
    """Set up tool logger."""
    if not config.enable_tool_logging:
        return
        
    logger = logging.getLogger("deer_flow.tools")
    logger.setLevel(getattr(logging, config.tool_log_level))
    logger.propagate = False
    
    handler = DateRotatingFileHandler(
        Path(config.log_dir) / "tools" / "tools.log",
        max_files=config.max_log_files
    )
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)


def _setup_performance_logger(config: LoggingConfig) -> None:
    """Set up performance logger."""
    if not config.enable_performance_logging:
        return
        
    logger = logging.getLogger("deer_flow.performance")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    handler = DateRotatingFileHandler(
        Path(config.log_dir) / "performance" / "performance.log",
        max_files=config.max_log_files
    )
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)


def _setup_security_logger(config: LoggingConfig) -> None:
    """Set up security logger."""
    if not config.enable_security_logging:
        return
        
    logger = logging.getLogger("deer_flow.security")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    handler = DateRotatingFileHandler(
        Path(config.log_dir) / "security" / "security.log",
        max_files=config.max_log_files
    )
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)