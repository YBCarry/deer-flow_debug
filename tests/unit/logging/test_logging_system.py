# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Tests for DeerFlow logging system.
"""

import json
import logging
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.logging import (
    LoggingConfig,
    setup_logging,
    InteractionLogger,
    get_interaction_logger,
    log_interaction,
    log_agent_activity,
    log_workflow_event,
    log_tool_usage,
)
from src.logging.handlers import DateRotatingFileHandler
from src.logging.formatters import StructuredFormatter, InteractionFormatter


class TestLoggingConfig:
    """Test logging configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = LoggingConfig()
        assert config.log_dir == "logs"
        assert config.enable_interaction_logging is True
        assert config.max_log_files == 30
        assert config.enable_performance_logging is True
    
    def test_from_env(self):
        """Test configuration from environment variables."""
        env_vars = {
            "DEER_FLOW_LOG_DIR": "/tmp/test_logs",
            "DEER_FLOW_LOG_INTERACTIONS": "false",
            "DEER_FLOW_INTERACTION_LOG_LEVEL": "DEBUG",
            "DEER_FLOW_MAX_LOG_FILES": "7",
        }
        
        with patch.dict(os.environ, env_vars):
            config = LoggingConfig.from_env()
            assert config.log_dir == "/tmp/test_logs"
            assert config.enable_interaction_logging is False
            assert config.interaction_log_level == "DEBUG"
            assert config.max_log_files == 7


class TestDateRotatingFileHandler:
    """Test date rotating file handler."""
    
    def test_handler_creation(self):
        """Test handler creates dated filenames correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_file = Path(temp_dir) / "test.log"
            handler = DateRotatingFileHandler(base_file, max_files=5)
            
            # Check that the file was created with date suffix
            today = datetime.now().date().strftime("%Y-%m-%d")
            expected_file = Path(temp_dir) / f"test_{today}.log"
            assert expected_file.exists()
            
            handler.close()
    
    def test_file_rotation(self):
        """Test that files rotate when date changes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_file = Path(temp_dir) / "test.log"
            handler = DateRotatingFileHandler(base_file, max_files=5)
            
            # Mock date change
            old_date = handler.current_date
            handler.current_date = datetime(2025, 1, 1).date()
            
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=0,
                msg="test message", args=(), exc_info=None
            )
            
            handler.emit(record)
            
            # Should create new file for new date
            new_file = Path(temp_dir) / "test_2025-01-01.log"
            assert new_file.exists()
            
            handler.close()


class TestStructuredFormatter:
    """Test structured JSON formatter."""
    
    def test_basic_formatting(self):
        """Test basic log record formatting."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test.logger", level=logging.INFO, pathname="/test/path.py",
            lineno=42, msg="Test message", args=(), exc_info=None
        )
        
        formatted = formatter.format(record)
        data = json.loads(formatted)
        
        assert data["level"] == "INFO"
        assert data["logger"] == "test.logger"
        assert data["message"] == "Test message"
        assert data["line"] == 42
        assert "timestamp" in data
    
    def test_custom_fields(self):
        """Test formatting with custom fields."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test.logger", level=logging.INFO, pathname="/test/path.py",
            lineno=42, msg="Test message", args=(), exc_info=None
        )
        record.session_id = "test-session-123"
        record.custom_field = "custom_value"
        
        formatted = formatter.format(record)
        data = json.loads(formatted)
        
        assert data["session_id"] == "test-session-123"
        assert data["custom_field"] == "custom_value"


class TestInteractionLogger:
    """Test interaction logger functionality."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Provide temporary log directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def logger_with_temp_dir(self, temp_log_dir):
        """Provide interaction logger with temporary directory."""
        config = LoggingConfig(log_dir=temp_log_dir)
        setup_logging(config)
        return InteractionLogger("test-session-123")
    
    def test_log_interaction(self, logger_with_temp_dir):
        """Test interaction logging."""
        logger = logger_with_temp_dir
        
        event_id = logger.log_interaction(
            event_type="user_query",
            user_input="What is the weather today?",
            agent_response="The weather is sunny.",
            agent_name="weather_agent",
            duration_ms=150.5,
            metadata={"location": "New York"}
        )
        
        assert event_id is not None
        assert len(event_id) > 0
    
    def test_log_agent_activity(self, logger_with_temp_dir):
        """Test agent activity logging."""
        logger = logger_with_temp_dir
        
        event_id = logger.log_agent_activity(
            agent_name="researcher",
            activity_type="web_search",
            llm_model="gpt-4",
            prompt_tokens=100,
            completion_tokens=200,
            duration_ms=500.0,
            input_data="search query",
            output_data="search results",
            metadata={"search_engine": "tavily"}
        )
        
        assert event_id is not None
        assert len(event_id) > 0
    
    def test_log_workflow_event(self, logger_with_temp_dir):
        """Test workflow event logging.""" 
        logger = logger_with_temp_dir
        
        event_id = logger.log_workflow_event(
            workflow_type="research_workflow",
            node_name="planner",
            status="completed",
            input_data={"query": "test query"},
            output_data={"plan": "test plan"},
            duration_ms=300.0
        )
        
        assert event_id is not None
        assert len(event_id) > 0
    
    def test_log_tool_usage(self, logger_with_temp_dir):
        """Test tool usage logging."""
        logger = logger_with_temp_dir
        
        event_id = logger.log_tool_usage(
            tool_name="web_search",
            input_parameters={"query": "test", "max_results": 5},
            output_result="search results",
            agent_name="researcher",
            duration_ms=200.0,
            success=True
        )
        
        assert event_id is not None
        assert len(event_id) > 0
    
    def test_log_tool_usage_error(self, logger_with_temp_dir):
        """Test tool usage error logging."""
        logger = logger_with_temp_dir
        
        event_id = logger.log_tool_usage(
            tool_name="web_search",
            input_parameters={"query": "test"},
            agent_name="researcher",
            duration_ms=100.0,
            success=False,
            error="API rate limit exceeded"
        )
        
        assert event_id is not None
        assert len(event_id) > 0
    
    def test_timing_context_manager(self, logger_with_temp_dir):
        """Test timing context manager."""
        logger = logger_with_temp_dir
        
        with logger.timing("test_operation"):
            time.sleep(0.1)  # Simulate work
        
        # Should have logged performance metric (we can't easily verify this without
        # checking log files, but we can verify it doesn't crash)
    
    def test_log_performance_metric(self, logger_with_temp_dir):
        """Test performance metric logging."""
        logger = logger_with_temp_dir
        
        # This should not raise an exception
        logger.log_performance_metric(
            metric_name="response_time",
            value=150.5,
            unit="ms",
            metadata={"endpoint": "/api/chat"}
        )
    
    def test_log_security_event(self, logger_with_temp_dir):
        """Test security event logging."""
        logger = logger_with_temp_dir
        
        # This should not raise an exception
        logger.log_security_event(
            event_type="authentication_failure",
            description="Invalid API key provided",
            severity="WARNING",
            user_id="user123",
            ip_address="192.168.1.1",
            metadata={"endpoint": "/api/chat"}
        )


class TestGlobalFunctions:
    """Test global convenience functions."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Provide temporary log directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = LoggingConfig(log_dir=temp_dir)
            setup_logging(config)
            yield temp_dir
    
    def test_get_interaction_logger(self, temp_log_dir):
        """Test getting global interaction logger."""
        logger1 = get_interaction_logger("session-123")
        logger2 = get_interaction_logger("session-123")
        
        # Should return same instance for same session
        assert logger1 is logger2
        assert logger1.session_id == "session-123"
        
        # Different session should create new instance
        logger3 = get_interaction_logger("session-456")
        assert logger3 is not logger1
        assert logger3.session_id == "session-456"
    
    def test_convenience_functions(self, temp_log_dir):
        """Test convenience logging functions."""
        session_id = "test-session"
        
        # Test interaction logging
        event_id1 = log_interaction(
            event_type="test",
            user_input="test input",
            session_id=session_id
        )
        assert event_id1 is not None
        
        # Test agent activity logging
        event_id2 = log_agent_activity(
            agent_name="test_agent",
            activity_type="test_activity",
            session_id=session_id
        )
        assert event_id2 is not None
        
        # Test workflow event logging
        event_id3 = log_workflow_event(
            workflow_type="test_workflow",
            node_name="test_node",
            status="completed",
            session_id=session_id
        )
        assert event_id3 is not None
        
        # Test tool usage logging
        event_id4 = log_tool_usage(
            tool_name="test_tool",
            success=True,
            session_id=session_id
        )
        assert event_id4 is not None


class TestLogFileCreation:
    """Test that log files are created correctly."""
    
    def test_setup_logging_creates_directories(self):
        """Test that setup_logging creates all required directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = LoggingConfig(log_dir=temp_dir)
            setup_logging(config)
            
            # Check all subdirectories are created
            expected_dirs = [
                "interactions", "agents", "workflows", "tools", 
                "system", "performance", "security"
            ]
            
            for dir_name in expected_dirs:
                assert (Path(temp_dir) / dir_name).exists()
                assert (Path(temp_dir) / dir_name).is_dir()
    
    def test_log_files_are_created_with_dates(self):
        """Test that actual logging creates dated files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = LoggingConfig(log_dir=temp_dir)
            setup_logging(config)
            
            # Generate some log entries
            logger = get_interaction_logger("test-session")
            logger.log_interaction(
                event_type="test",
                user_input="test message"
            )
            
            # Check that interaction log file was created
            interactions_dir = Path(temp_dir) / "interactions"
            log_files = list(interactions_dir.glob("interactions_*.log"))
            assert len(log_files) > 0
            
            # Check filename contains date
            today = datetime.now().date().strftime("%Y-%m-%d")
            expected_file = interactions_dir / f"interactions_{today}.log"
            assert expected_file.exists()


@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration tests for complete logging scenarios."""
    
    def test_full_interaction_logging_scenario(self):
        """Test a complete user interaction scenario with logging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = LoggingConfig(log_dir=temp_dir)
            setup_logging(config)
            
            session_id = "integration-test-session"
            
            # Simulate complete interaction flow
            # 1. User query
            log_interaction(
                event_type="user_query",
                user_input="What is machine learning?",
                session_id=session_id
            )
            
            # 2. Workflow starts
            log_workflow_event(
                workflow_type="research_workflow", 
                node_name="start",
                status="started",
                session_id=session_id
            )
            
            # 3. Planner activity
            log_agent_activity(
                agent_name="planner",
                activity_type="plan_generation",
                llm_model="gpt-4",
                prompt_tokens=150,
                completion_tokens=80,
                duration_ms=800.0,
                session_id=session_id
            )
            
            # 4. Tool usage
            log_tool_usage(
                tool_name="web_search",
                agent_name="researcher",
                input_parameters={"query": "machine learning basics"},
                duration_ms=500.0,
                success=True,
                session_id=session_id
            )
            
            # 5. Agent response
            log_interaction(
                event_type="agent_response",
                agent_response="Machine learning is a subset of artificial intelligence...",
                agent_name="researcher",
                duration_ms=1200.0,
                session_id=session_id
            )
            
            # 6. Workflow completion
            log_workflow_event(
                workflow_type="research_workflow",
                node_name="complete",
                status="completed",
                duration_ms=2500.0,
                session_id=session_id
            )
            
            # Verify log files were created
            log_dir = Path(temp_dir)
            assert (log_dir / "interactions").exists()
            assert (log_dir / "agents").exists() 
            assert (log_dir / "workflows").exists()
            assert (log_dir / "tools").exists()
            
            # Check that files have content
            today = datetime.now().date().strftime("%Y-%m-%d")
            interaction_file = log_dir / "interactions" / f"interactions_{today}.log"
            if interaction_file.exists():
                assert interaction_file.stat().st_size > 0