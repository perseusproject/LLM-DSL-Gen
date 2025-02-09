# -*- coding: utf-8 -*-
# dsl_gen/agents/lokad_compiler.py
# dsl_gen/agents/lokad_compiler.py
from typing import Dict, Any
import requests
import logging
from ..core.rag import RAGState
from ..config import CFG
from langgraph.graph import END

logger = logging.getLogger('dsl_gen')


def check_compilation(script: str) -> Dict[str, Any]:
    """
    Checks the compilation of a given script using the Lokad TryCompile service.
    Args:
        script (str): The script to be compiled.
    Returns:
        Dict[str, Any]: A dictionary containing the compilation result:
            - "valid" (bool): True if the compilation is successful, False otherwise.
            - "messages" (list): A list of error messages if the compilation fails.
    Raises:
        Exception: If there is a connection error or the service is unavailable.
    """

    logger.debug("Checking compilation for script:\n%s", script)

    url = "https://try.lokad.com/w/script/trycompile"
    payload = {"Script": script}

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result["IsCompOk"]:
                logger.debug("Compilation successful")
                return {
                    "valid": True,
                    "messages": [],
                }
            logger.debug("Compilation failed")
            errors = [
                f"Line {msg['Line']}: {msg['Text']} (Severity: {msg['Severity']})"
                for msg in result.get("CompMessages", [])
            ]
            return {"valid": False, "messages": errors}

        logger.error('Compilation service unavailable (HTTP %s)',
                     response.status_code)
        return {
            "valid": False,
            "messages": [f"Service unavailable (HTTP {response.status_code})"],
        }

    except Exception as e:
        logger.error('Connection error: %s', str(e))
        return {
            "valid": False,
            "messages": [f"Connection error: {str(e)}"]
        }


def compile_code(state: RAGState) -> RAGState:
    """Compiler node
    ### Input fields
        question_type (str): The type of question (QA or coding)
        completion (str): The code to be compiled.
    ### Fields modified
        compilation_result (dict): Last compilation result.
        compilation_attempts (int): Number of compilation attempts.
    """

    if state["question_type"] == "QA":
        logger.debug("Skipping compilation for QA question")
        return {**state, "compilation": {"valid": True, "errors": [], "raw_data": None, "attempt": 0}}

    assert "completion" in state, "completion field is required"

    code = state.get("completion", "")

    current_attempt = state.get("compilation_attempts", 0) + 1

    compilation_result = check_compilation(code)

    # Log compilation results
    if not compilation_result["valid"]:
        logger.warning(
            f"Compilation failed (Attempt {current_attempt}):\n{code}")
        logger.debug(f"Compilation errors: {compilation_result['messages']}")
    else:
        logger.info(f"Code compiled successfully (Attempt {current_attempt})")

    state.update({
        "compilation_result": compilation_result,
        "compilation_attempts": current_attempt,
        "final_state": "compilation error" if not compilation_result["valid"] else "pending"
    })
    return state


__all__ = ["compile_code", "handle_compilation"]
