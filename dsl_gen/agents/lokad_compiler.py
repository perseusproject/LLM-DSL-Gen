# -*- coding: utf-8 -*-
# dsl_gen/agents/lokad_compiler.py
# dsl_gen/agents/lokad_compiler.py
from typing import Dict, Any
import requests
import logging
from dsl_gen.core.rag import RAGState

logger = logging.getLogger('dsl_gen')


def check_compilation(script: str) -> Dict[str, Any]:
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
    """与流程引擎深度集成的编译器节点"""
    code = state.get("answer", "")

    # 执行编译检查
    compilation_result = check_compilation(code)

    # 构建状态更新
    state_updates = {
        "compilation": {
            "valid": compilation_result["valid"],
            "errors": compilation_result["messages"],
            "raw_data": compilation_result["raw_output"]
        },
        "error": None if compilation_result["valid"] else "; ".join(compilation_result["messages"])
    }

    # 记录诊断日志
    if not compilation_result["valid"]:
        logger.warning(f"Compilation failed for code:\n{code}")
        logger.debug(f"Compilation errors: {compilation_result['messages']}")
    else:
        logger.info("Code compiled successfully")

    return {**state, **state_updates}
