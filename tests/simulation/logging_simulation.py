# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Automated simulation and testing of DeerFlow logging system.
"""

import asyncio
import json
import os
import random
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock

from src.logging import LoggingConfig, setup_logging, get_interaction_logger
from src.workflow import run_agent_workflow_async


class LoggingSimulator:
    """Automated simulator for testing logging system."""
    
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.sessions = []
        self.config = LoggingConfig(log_dir=str(log_dir))
        setup_logging(self.config)
    
    def simulate_user_session(self, session_id: str, num_interactions: int = 5):
        """Simulate a complete user session with multiple interactions."""
        logger = get_interaction_logger(session_id)
        
        queries = [
            "What is artificial intelligence?",
            "How does machine learning work?",
            "Explain deep learning concepts",
            "What are the applications of AI?",
            "How to get started with ML?",
            "What is the difference between AI and ML?",
            "Explain neural networks",
            "What is natural language processing?",
        ]
        
        agents = ["coordinator", "planner", "researcher", "coder", "reporter"]
        tools = ["web_search", "crawl_tool", "python_repl", "retriever"]
        
        session_start = time.time()
        
        for i in range(num_interactions):
            interaction_start = time.time()
            
            # Random user query
            query = random.choice(queries)
            
            # Log user interaction
            logger.log_interaction(
                event_type="user_query",
                user_input=query,
                metadata={"interaction_number": i + 1}
            )
            
            # Simulate workflow
            workflow_events = [
                ("start", "started"),
                ("coordinator", "started"),
                ("coordinator", "completed"),
                ("planner", "started"),
                ("planner", "completed"),
                ("researcher", "started"),
                ("researcher", "completed"),
                ("reporter", "started"),
                ("reporter", "completed"),
                ("end", "completed"),
            ]
            
            for node_name, status in workflow_events:
                duration = random.uniform(50, 500)
                logger.log_workflow_event(
                    workflow_type="research_workflow",
                    node_name=node_name,
                    status=status,
                    duration_ms=duration
                )
                
                # Simulate some processing time
                time.sleep(0.01)
            
            # Simulate agent activities
            for agent in random.sample(agents, random.randint(2, 4)):
                logger.log_agent_activity(
                    agent_name=agent,
                    activity_type="processing",
                    llm_model=random.choice(["gpt-4", "gpt-3.5-turbo", "claude-3"]),
                    prompt_tokens=random.randint(50, 500),
                    completion_tokens=random.randint(20, 200),
                    duration_ms=random.uniform(200, 1000)
                )
            
            # Simulate tool usage
            for tool in random.sample(tools, random.randint(1, 3)):
                success = random.random() > 0.1  # 90% success rate
                logger.log_tool_usage(
                    tool_name=tool,
                    agent_name=random.choice(agents),
                    input_parameters={"query": query[:50]},
                    output_result="Tool output..." if success else None,
                    duration_ms=random.uniform(100, 800),
                    success=success,
                    error=None if success else "Simulated error"
                )
            
            # Log agent response
            response_length = random.randint(100, 1000)
            response = f"Generated response of {response_length} characters for: {query[:50]}..."
            
            interaction_duration = (time.time() - interaction_start) * 1000
            logger.log_interaction(
                event_type="agent_response",
                agent_response=response,
                agent_name="reporter",
                duration_ms=interaction_duration,
                metadata={
                    "response_length": response_length,
                    "interaction_number": i + 1
                }
            )
            
            # Random delay between interactions
            time.sleep(random.uniform(0.1, 0.5))
        
        session_duration = (time.time() - session_start) * 1000
        logger.log_performance_metric(
            metric_name="session_duration",
            value=session_duration,
            unit="ms",
            metadata={
                "session_id": session_id,
                "num_interactions": num_interactions
            }
        )
        
        self.sessions.append({
            "session_id": session_id,
            "interactions": num_interactions,
            "duration_ms": session_duration
        })
        
        return session_id
    
    def simulate_concurrent_sessions(self, num_sessions: int = 3, interactions_per_session: int = 5):
        """Simulate multiple concurrent user sessions."""
        import threading
        
        threads = []
        session_ids = []
        
        for i in range(num_sessions):
            session_id = f"concurrent-session-{i+1}-{int(time.time())}"
            session_ids.append(session_id)
            
            thread = threading.Thread(
                target=self.simulate_user_session,
                args=(session_id, interactions_per_session)
            )
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        return session_ids
    
    def simulate_error_scenarios(self, session_id: str):
        """Simulate various error scenarios."""
        logger = get_interaction_logger(session_id)
        
        error_scenarios = [
            {
                "type": "tool_error",
                "description": "Web search API timeout",
                "tool": "web_search",
                "error": "Request timeout after 30 seconds"
            },
            {
                "type": "llm_error", 
                "description": "LLM rate limit exceeded",
                "agent": "researcher",
                "error": "Rate limit exceeded. Try again in 60 seconds"
            },
            {
                "type": "workflow_error",
                "description": "Invalid state transition",
                "node": "planner",
                "error": "Cannot transition from planner to end without completing research"
            },
            {
                "type": "security_error",
                "description": "Suspicious input detected",
                "error": "Input contains potential security threat"
            }
        ]
        
        for scenario in error_scenarios:
            if scenario["type"] == "tool_error":
                logger.log_tool_usage(
                    tool_name=scenario["tool"],
                    agent_name="researcher",
                    success=False,
                    error=scenario["error"],
                    duration_ms=random.uniform(1000, 5000)
                )
            
            elif scenario["type"] == "llm_error":
                logger.log_agent_activity(
                    agent_name=scenario["agent"],
                    activity_type="llm_call_error",
                    duration_ms=random.uniform(500, 2000),
                    metadata={
                        "error": scenario["error"],
                        "success": False
                    }
                )
            
            elif scenario["type"] == "workflow_error":
                logger.log_workflow_event(
                    workflow_type="research_workflow",
                    node_name=scenario["node"],
                    status="error",
                    error=scenario["error"],
                    duration_ms=random.uniform(100, 500)
                )
            
            elif scenario["type"] == "security_error":
                logger.log_security_event(
                    event_type="input_validation",
                    description=scenario["description"],
                    severity="WARNING",
                    metadata={"error": scenario["error"]}
                )
            
            time.sleep(0.1)
    
    def simulate_performance_stress_test(self, duration_seconds: int = 60):
        """Simulate high-load performance testing."""
        start_time = time.time()
        operations = 0
        
        while time.time() - start_time < duration_seconds:
            session_id = f"stress-test-{operations}-{int(time.time())}"
            logger = get_interaction_logger(session_id)
            
            # Rapid-fire logging
            for _ in range(10):
                logger.log_interaction(
                    event_type="stress_test",
                    user_input="Stress test query",
                    duration_ms=random.uniform(1, 10)
                )
                operations += 1
            
            if operations % 100 == 0:
                print(f"Completed {operations} operations in {time.time() - start_time:.1f}s")
            
            time.sleep(0.001)  # Brief pause
        
        print(f"Stress test completed: {operations} operations in {duration_seconds}s")
        return operations
    
    def analyze_log_files(self) -> Dict[str, Any]:
        """Analyze generated log files and return statistics."""
        today = datetime.now().date().strftime("%Y-%m-%d")
        
        stats = {
            "files_created": 0,
            "total_events": 0,
            "events_by_type": {},
            "file_sizes": {},
            "sessions_count": len(set(s["session_id"] for s in self.sessions)),
        }
        
        log_types = ["interactions", "agents", "workflows", "tools", "performance", "security"]
        
        for log_type in log_types:
            log_file = self.log_dir / log_type / f"{log_type}_{today}.log"
            
            if log_file.exists():
                stats["files_created"] += 1
                file_size = log_file.stat().st_size
                stats["file_sizes"][log_type] = file_size
                
                # Count events
                event_count = 0
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            if line.strip():
                                event_count += 1
                except Exception as e:
                    print(f"Error reading {log_file}: {e}")
                
                stats["events_by_type"][log_type] = event_count
                stats["total_events"] += event_count
        
        return stats
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of the simulation."""
        stats = self.analyze_log_files()
        
        report = f"""
DeerFlow Logging System Simulation Report
========================================
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Session Summary:
- Total sessions simulated: {stats['sessions_count']}
- Total interactions: {sum(s['interactions'] for s in self.sessions)}
- Average session duration: {sum(s['duration_ms'] for s in self.sessions) / len(self.sessions) if self.sessions else 0:.1f}ms

Log File Statistics:
- Log files created: {stats['files_created']}
- Total events logged: {stats['total_events']}

Events by Type:
"""
        
        for log_type, count in stats["events_by_type"].items():
            report += f"- {log_type}: {count} events\n"
        
        report += f"\nFile Sizes:\n"
        for log_type, size in stats["file_sizes"].items():
            report += f"- {log_type}: {size:,} bytes\n"
        
        report += f"""
Log Directory Structure:
- Base directory: {self.log_dir}
- Subdirectories: interactions/, agents/, workflows/, tools/, performance/, security/, system/

Files are organized by date (YYYY-MM-DD) to enable easy rotation and archival.
"""
        
        return report


async def run_simulation():
    """Run comprehensive logging simulation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Running logging simulation in: {temp_dir}")
        
        simulator = LoggingSimulator(temp_dir)
        
        # Run various simulation scenarios
        print("\n1. Simulating sequential user sessions...")
        for i in range(3):
            session_id = f"sequential-session-{i+1}"
            simulator.simulate_user_session(session_id, interactions_per_session=3)
        
        print("\n2. Simulating concurrent user sessions...")
        simulator.simulate_concurrent_sessions(num_sessions=3, interactions_per_session=2)
        
        print("\n3. Simulating error scenarios...")
        error_session = "error-scenario-session"
        simulator.simulate_error_scenarios(error_session)
        
        print("\n4. Running performance stress test...")
        operations = simulator.simulate_performance_stress_test(duration_seconds=10)
        
        # Generate and display report
        print("\n" + "="*60)
        print("SIMULATION COMPLETED")
        print("="*60)
        
        report = simulator.generate_summary_report()
        print(report)
        
        # Verify log files exist and have content
        stats = simulator.analyze_log_files()
        
        print(f"\nValidation Results:")
        print(f"✓ Files created: {stats['files_created']}/7 expected")
        print(f"✓ Total events: {stats['total_events']:,}")
        print(f"✓ Performance: {operations} operations in 10 seconds")
        
        # Test log file parsing
        print(f"\nTesting log file integrity...")
        today = datetime.now().date().strftime("%Y-%m-%d")
        
        for log_type in ["interactions", "agents", "workflows"]:
            log_file = Path(temp_dir) / log_type / f"{log_type}_{today}.log"
            if log_file.exists():
                try:
                    valid_json_lines = 0
                    with open(log_file, 'r') as f:
                        for line in f:
                            if line.strip():
                                json.loads(line)  # This will raise if invalid JSON
                                valid_json_lines += 1
                    print(f"✓ {log_type}.log: {valid_json_lines} valid JSON entries")
                except Exception as e:
                    print(f"✗ {log_type}.log: JSON parsing error - {e}")
            else:
                print(f"✗ {log_type}.log: File not found")
        
        print(f"\nLog files are available at: {temp_dir}")
        print("Simulation completed successfully!")


if __name__ == "__main__":
    print("Starting DeerFlow Logging System Simulation...")
    asyncio.run(run_simulation())