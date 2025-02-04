# -*- coding: utf-8 -*-
# dsl_gen/agents/lokad_compiler.py
# dsl_gen/agents/lokad_compiler.py
from typing import Dict, Any
import requests
import logging
from dsl_gen.core.rag import RAGState
from dsl_gen import CFG
from langgraph.graph import END

logger = logging.getLogger('dsl_gen')


def check_compilation(script: str) -> Dict[str, Any]:

    logger.debug("Checking compilation for script:\n%s", script)

    """增强版编译检查，返回结构化结果"""
    url = "https://try.lokad.com/w/script/trycompile"
    payload = {"Script": script}

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if result["IsCompOk"]:
                return {
                    "valid": True,
                    "messages": [],
                    "raw_output": result
                }

            # 提取编译错误详情
            errors = [
                f"Line {msg['Line']}: {msg['Text']} (Severity: {msg['Severity']})"
                for msg in result.get("CompMessages", [])
            ]
            return {
                "valid": False,
                "messages": errors,
                "raw_output": result
            }

        return {
            "valid": False,
            "messages": [f"Service unavailable (HTTP {response.status_code})"],
            "raw_output": None
        }

    except Exception as e:
        return {
            "valid": False,
            "messages": [f"Connection error: {str(e)}"],
            "raw_output": None
        }


def compile_code(state: RAGState) -> RAGState:
    """compiler node"""
    if state["question_type"] == "QA":
        logger.debug("Skipping compilation for QA question")
        return {**state, "compilation": {"valid": True, "errors": [], "raw_data": None, "attempt": 0}}

    code = state.get("completion", "")
    current_attempt = state.get("compilation_attempts", 0) + 1

    # 执行编译检查
    compilation_result = check_compilation(code)

    state_updates = {
        "compilation": {
            "valid": compilation_result["valid"],
            "errors": compilation_result["messages"],
            "raw_data": compilation_result["raw_output"],
            "attempt": current_attempt
        },
        "compilation_attempts": current_attempt,
        "error": None if compilation_result["valid"] else f"Compilation failed (Attempt {current_attempt})"
    }

    # 记录诊断日志
    if not compilation_result["valid"]:
        logger.warning(
            f"Compilation failed (Attempt {current_attempt}):\n{code}")
        logger.debug(f"Compilation errors: {compilation_result['messages']}")
    else:
        logger.info(f"Code compiled successfully (Attempt {current_attempt})")

    state.update(state_updates)
    return state


def handle_compilation(state: RAGState) -> str:
    max_retries = CFG.COMPILER.max_retries
    # 如果编译成功或超过最大重试次数，进入judge环节
    if state["compilation"]["valid"]:
        return "judge"
    elif state["compilation_attempts"] >= max_retries:
        return END
    else:
        return "llm_coder"


__all__ = ["compile_code", "handle_compilation"]
