# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import time
from src.config.configuration import get_recursion_limit
from src.graph import build_graph
from src.logging import setup_logging, get_interaction_logger, log_workflow_event

# Setup comprehensive logging
setup_logging()

# Configure basic logging for backwards compatibility
logging.basicConfig(
    level=logging.INFO,  # Default level is INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def enable_debug_logging():
    """Enable debug level logging for more detailed execution information."""
    logging.getLogger("src").setLevel(logging.DEBUG)


logger = logging.getLogger(__name__)

# Create the graph
graph = build_graph()


async def run_agent_workflow_async(
    user_input: str,
    debug: bool = False,
    max_plan_iterations: int = 1,
    max_step_num: int = 3,
    enable_background_investigation: bool = True,
    session_id: str = None,
):
    """Run the agent workflow asynchronously with the given user input.

    Args:
        user_input: The user's query or request
        debug: If True, enables debug level logging
        max_plan_iterations: Maximum number of plan iterations
        max_step_num: Maximum number of steps in a plan
        enable_background_investigation: If True, performs web search before planning to enhance context
        session_id: Optional session ID for logging

    Returns:
        The final state after the workflow completes
    """
    if not user_input:
        raise ValueError("Input could not be empty")

    if debug:
        enable_debug_logging()

    # Initialize interaction logger
    interaction_logger = get_interaction_logger(session_id)
    
    # Log workflow start
    workflow_start_time = time.time()
    start_event_id = log_workflow_event(
        workflow_type="research_workflow",
        node_name="start",
        status="started",
        input_data={"user_input": user_input[:500] + "..." if len(user_input) > 500 else user_input}
    )

    logger.info(f"Starting async workflow with user input: {user_input}")
    initial_state = {
        # Runtime Variables
        "messages": [{"role": "user", "content": user_input}],
        "auto_accepted_plan": True,
        "enable_background_investigation": enable_background_investigation,
    }
    config = {
        "configurable": {
            "thread_id": "default",
            "max_plan_iterations": max_plan_iterations,
            "max_step_num": max_step_num,
            "mcp_settings": {
                "servers": {
                    "mcp-github-trending": {
                        "transport": "stdio",
                        "command": "uvx",
                        "args": ["mcp-github-trending"],
                        "enabled_tools": ["get_github_trending_repositories"],
                        "add_to_agents": ["researcher"],
                    }
                }
            },
        },
        "recursion_limit": get_recursion_limit(default=100),
    }
    last_message_cnt = 0
    try:
        async for s in graph.astream(
            input=initial_state, config=config, stream_mode="values"
        ):
            try:
                if isinstance(s, dict) and "messages" in s:
                    if len(s["messages"]) <= last_message_cnt:
                        continue
                    last_message_cnt = len(s["messages"])
                    message = s["messages"][-1]
                    
                    # Log the interaction
                    interaction_logger.log_interaction(
                        event_type="agent_message",
                        agent_response=str(message) if hasattr(message, '__str__') else repr(message),
                        metadata={"message_count": len(s["messages"])}
                    )
                    
                    if isinstance(message, tuple):
                        print(message)
                    else:
                        message.pretty_print()
                else:
                    # For any other output format
                    print(f"Output: {s}")
            except Exception as e:
                logger.error(f"Error processing stream output: {e}")
                interaction_logger.log_interaction(
                    event_type="stream_error",
                    error=str(e),
                    metadata={"output": str(s)[:500]}
                )
                print(f"Error processing output: {str(e)}")

        # Log successful completion
        workflow_duration = (time.time() - workflow_start_time) * 1000
        log_workflow_event(
            workflow_type="research_workflow",
            node_name="complete",
            status="completed",
            duration_ms=workflow_duration
        )
        
        logger.info("Async workflow completed successfully")

    except Exception as e:
        # Log workflow error
        workflow_duration = (time.time() - workflow_start_time) * 1000
        log_workflow_event(
            workflow_type="research_workflow",
            node_name="error",
            status="error",
            duration_ms=workflow_duration,
            error=str(e)
        )
        logger.error(f"Workflow failed: {e}")
        raise


if __name__ == "__main__":
    print(graph.get_graph(xray=True).draw_mermaid())
