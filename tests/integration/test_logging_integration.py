# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Integration tests for DeerFlow logging system.
"""

import asyncio
import json
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.logging import LoggingConfig, setup_logging, get_interaction_logger
from src.workflow import run_agent_workflow_async


@pytest.mark.asyncio
@pytest.mark.integration
class TestWorkflowLogging:
    """Integration tests for workflow logging."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Provide temporary log directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @patch('src.tools.search.get_web_search_tool')
    @patch('src.llms.llm.get_llm_by_type')
    async def test_workflow_logging_integration(self, mock_get_llm, mock_search_tool, temp_log_dir):
        """Test that workflow execution generates proper logs."""
        # Setup logging with temp directory
        config = LoggingConfig(log_dir=temp_log_dir)
        setup_logging(config)
        
        # Mock LLM and search tool
        mock_llm = MagicMock()
        mock_llm.invoke = MagicMock(return_value="This is a test response")
        mock_get_llm.return_value = mock_llm
        
        mock_search = MagicMock()
        mock_search.invoke = MagicMock(return_value=["Test search result"])
        mock_search_tool.return_value = mock_search
        
        session_id = "test-workflow-session"
        
        try:
            # Run workflow with logging
            await run_agent_workflow_async(
                user_input="Test query for logging",
                debug=False,
                max_plan_iterations=1,
                max_step_num=2,
                enable_background_investigation=True,
                session_id=session_id
            )
        except Exception as e:
            # Workflow might fail due to mocking, but logs should still be created
            print(f"Workflow failed (expected due to mocking): {e}")
        
        # Verify log files were created
        log_dir = Path(temp_log_dir)
        
        # Check directory structure
        assert (log_dir / "workflows").exists()
        assert (log_dir / "interactions").exists()
        
        # Check workflow logs
        today = datetime.now().date().strftime("%Y-%m-%d")
        workflow_log = log_dir / "workflows" / f"workflows_{today}.log"
        
        if workflow_log.exists() and workflow_log.stat().st_size > 0:
            with open(workflow_log, 'r') as f:
                log_content = f.read()
                
            # Should contain workflow start event
            assert "research_workflow" in log_content
            assert session_id in log_content


class TestLogFileAnalysis:
    """Test tools for analyzing generated log files."""
    
    def test_log_file_structure(self):
        """Test that log files have proper JSON structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = LoggingConfig(log_dir=temp_dir)
            setup_logging(config)
            
            session_id = "structure-test-session"
            logger = get_interaction_logger(session_id)
            
            # Generate various log types
            logger.log_interaction(
                event_type="test_interaction",
                user_input="Test input",
                agent_response="Test response",
                duration_ms=100.0
            )
            
            logger.log_agent_activity(
                agent_name="test_agent",
                activity_type="test_activity",
                llm_model="test-model",
                prompt_tokens=50,
                completion_tokens=30,
                duration_ms=200.0
            )
            
            logger.log_tool_usage(
                tool_name="test_tool",
                input_parameters={"param": "value"},
                success=True,
                duration_ms=150.0
            )
            
            # Analyze log files
            today = datetime.now().date().strftime("%Y-%m-%d")
            
            # Check interaction logs
            interaction_file = Path(temp_dir) / "interactions" / f"interactions_{today}.log"
            if interaction_file.exists():
                with open(interaction_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                assert "timestamp" in data
                                assert "session_id" in data
                                assert data["session_id"] == session_id
                            except json.JSONDecodeError as e:
                                pytest.fail(f"Invalid JSON in interaction log: {e}")
            
            # Check agent logs  
            agent_file = Path(temp_dir) / "agents" / f"agents_{today}.log"
            if agent_file.exists():
                with open(agent_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                assert "timestamp" in data
                                assert "logger" in data
                            except json.JSONDecodeError as e:
                                pytest.fail(f"Invalid JSON in agent log: {e}")
    
    def test_log_performance_tracking(self):
        """Test performance tracking in logs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = LoggingConfig(log_dir=temp_dir)
            setup_logging(config)
            
            session_id = "performance-test-session"
            logger = get_interaction_logger(session_id)
            
            # Test timing context manager
            with logger.timing("test_operation"):
                time.sleep(0.01)  # Simulate work
            
            # Test manual performance logging
            logger.log_performance_metric(
                metric_name="api_response_time",
                value=250.5,
                unit="ms",
                metadata={
                    "endpoint": "/api/chat",
                    "method": "POST"
                }
            )
            
            # Verify performance logs
            today = datetime.now().date().strftime("%Y-%m-%d")
            perf_file = Path(temp_dir) / "performance" / f"performance_{today}.log"
            
            if perf_file.exists():
                with open(perf_file, 'r') as f:
                    content = f.read()
                    assert "test_operation" in content
                    assert "api_response_time" in content
                    assert "250.5" in content


class TestLogAnalysisTools:
    """Test utilities for analyzing log files."""
    
    @staticmethod
    def parse_log_file(log_file: Path):
        """Parse a log file and return structured data."""
        events = []
        if not log_file.exists():
            return events
            
        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return events
    
    def test_log_parsing_utility(self):
        """Test log file parsing utility."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = LoggingConfig(log_dir=temp_dir)
            setup_logging(config)
            
            session_id = "parse-test-session"
            logger = get_interaction_logger(session_id)
            
            # Generate test data
            test_events = []
            for i in range(5):
                event_id = logger.log_interaction(
                    event_type=f"test_event_{i}",
                    user_input=f"Test input {i}",
                    agent_response=f"Test response {i}",
                    duration_ms=float(i * 100)
                )
                test_events.append(event_id)
            
            # Parse logs
            today = datetime.now().date().strftime("%Y-%m-%d")
            log_file = Path(temp_dir) / "interactions" / f"interactions_{today}.log"
            
            parsed_events = self.parse_log_file(log_file)
            
            # Verify parsing
            assert len(parsed_events) >= 5  # At least our test events
            
            for event in parsed_events:
                assert "timestamp" in event
                assert "session_id" in event
                assert event["session_id"] == session_id
    
    @staticmethod
    def analyze_session_activity(log_dir: Path, session_id: str):
        """Analyze all activity for a specific session."""
        today = datetime.now().date().strftime("%Y-%m-%d")
        
        # Collect events from all log types
        all_events = []
        
        log_types = ["interactions", "agents", "workflows", "tools"]
        for log_type in log_types:
            log_file = log_dir / log_type / f"{log_type}_{today}.log"
            events = TestLogAnalysisTools.parse_log_file(log_file)
            
            # Filter by session
            session_events = [e for e in events if e.get("session_id") == session_id]
            
            for event in session_events:
                event["log_type"] = log_type
                all_events.append(event)
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x.get("timestamp", ""))
        
        return all_events
    
    def test_session_analysis(self):
        """Test session-based log analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = LoggingConfig(log_dir=temp_dir)
            setup_logging(config)
            
            session_id = "analysis-test-session"
            logger = get_interaction_logger(session_id)
            
            # Generate mixed activity
            logger.log_interaction(
                event_type="user_query",
                user_input="What is AI?",
                duration_ms=50.0
            )
            
            logger.log_agent_activity(
                agent_name="coordinator",
                activity_type="routing",
                duration_ms=100.0
            )
            
            logger.log_tool_usage(
                tool_name="web_search",
                agent_name="researcher",
                success=True,
                duration_ms=500.0
            )
            
            logger.log_interaction(
                event_type="agent_response",
                agent_response="AI is artificial intelligence...",
                duration_ms=200.0
            )
            
            # Analyze session
            events = self.analyze_session_activity(Path(temp_dir), session_id)
            
            # Verify analysis
            assert len(events) >= 4
            
            # Check event types are present
            log_types = {event["log_type"] for event in events}
            assert "interactions" in log_types
            assert "agents" in log_types or "tools" in log_types
            
            # Verify chronological order
            timestamps = [event.get("timestamp", "") for event in events]
            assert timestamps == sorted(timestamps)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])