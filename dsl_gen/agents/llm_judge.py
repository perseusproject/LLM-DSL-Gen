# -*- coding: utf-8 -*-
# dsl_gen/backend/llm_judge.py
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langgraph.graph import END
from .api import getClient
from dsl_gen import CFG
from dsl_gen.core.rag import RAGState
import logging

logger = logging.getLogger('dsl_gen')


def _build_judge_prompt(state: RAGState) -> list:
    """Structured scoring prompt template"""
    completion = state["completion"]
    is_code = state["question_type"] == "coding"
    ref = state.get("ref", "")
    ground_truth = state.get("ground_truth", None)
    errors = "; ".join(state.get("compilation", {}).get("errors", []))

    # Dynamically construct problem type description
    problem_type_desc = (
        "Code logic problem" if is_code else "Question answering problem",
        "(pay special attention to code logic)" if is_code else ""
    )

    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(CFG.JUDGE.personality),
        HumanMessagePromptTemplate.from_template(
            "## Problem Type\n{problem_type}\n\n"
            "## Original Question\n{question}\n\n"
            "## Answer\n```envision\n{completion}\n```\n\n"
            "## References Provided\n{ref}\n\n"
            "## Additional Reference (if provided)\n{ground_truth}\n\n"
            "Please analyze step by step and output the final judgment (0/1):"
        )
    ])

    return prompt_template.format_messages(
        problem_type=f"{problem_type_desc[0]}{problem_type_desc[1]}",
        question=state["question"],
        completion=completion,
        ref=ref,
        ground_truth=ground_truth or "No additional reference materials"
    )


def judge_answer(state: RAGState) -> RAGState:
    """Improved scoring node"""
    judgement_attempts = state.get("judge_attempts", 0) + 1

    try:
        # Generate structured prompt
        messages = _build_judge_prompt(state)

        # Call LLM and parse response
        client = getClient(CFG.JUDGE.active_model)
        response = client.invoke(messages)

        logger.info("Judgment: %s", response.content)

        # Extract final judgment from response
        last_line = response.content.strip().split('\n')[-1]
        judgment = 'correct' if '1' in last_line else 'incorrect'

        state.update({
            "judge_attempts": judgement_attempts,
            "judgment": judgment,
            "judge_output": response.content,
            "error": None if judgment == 1 else f"judgment failed on attempt {judgement_attempts}"
        })

        logger.info(f"Judgment: {judgment}")
        return state

    except Exception as e:
        logger.error(f"Judgment failed: {str(e)}")
        state.update({
            "judge_attempts": judgement_attempts,
            "judgment": "incorrect",
            "error": f"judgment exception {str(e)}"
        })
        return state


def handle_judgment(state: RAGState):
    """Enhanced judgment logic"""
    # Forced termination condition
    if state.get("judge_attempts", 0) >= CFG.JUDGE.max_retries:
        logger.warning("Reached maximum review attempts, forcing output")
        return END

    # Success condition
    if state.get("judgment") == "correct":
        logger.info("Answer passed quality check")
        return END

    # Failure retry logic
    logger.debug(
        f"Review attempt {state.get('judge_attempts', 0)} failed, regenerating answer")
    return {
        **state,
        # Clear historical generation traces
        "code": None,
        "compilation": None,
        "error": f"Iteration improvement in attempt {state.get('judge_attempts', 0)}..."
    }


__all__ = ["judge_answer", "handle_judgment"]
