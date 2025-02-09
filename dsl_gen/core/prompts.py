import logging
from ..config import CFG
from .state import RAGState
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage
from langchain_core.prompts import (ChatPromptTemplate,
                                    SystemMessagePromptTemplate,
                                    HumanMessagePromptTemplate)
from langchain_core.documents import Document
from typing import List

logger = logging.getLogger('dsl_gen')


def _format_context(docs: List[Document]) -> str:
    """Format the retrieved documents into a context string"""
    return "\n\n".join(
        f"Document {i+1} (from {doc.metadata.get('source', 'unknown')}):\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )


def generate_prompt(state: RAGState) -> RAGState:
    """Document retrieval node
    ### Input fields
        question (str): The question to be answered.
        question_type (str): The type of question (QA or coding)
        docs (List[Document]): The retrieved documents.
    ### Fields added
        messages (List[BaseMessage]): The formatted prompt messages.
    """
    assert ("question" in state) and (state["question"] is not None), \
        "Question must be provided in the state"
    assert ("question_type" in state) and (state["question_type"] is not None), \
        "Question type must be provided in the state"
    assert ("docs" in state) and (state["docs"] is not None), \
        "Retrieved documents must be provided in the state"

    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=CFG.CODER.personality),
        SystemMessagePromptTemplate.from_template(
            "Relevant Context:\n{context}\n\n"
            "Based on the above context and your knowledge, respond to:"
        ),
        HumanMessagePromptTemplate.from_template("{question}")
    ])

    # Format the context
    context = _format_context(state.get("docs", []))

    # Build the complete prompt
    formatted_prompt = prompt_template.format_messages(
        context=context,
        question=state["question"]
    )

    logger.debug(f"Generated prompt: {formatted_prompt[:100]}")

    # Changed to messages to be compatible with LCEL
    # LangChain Enhanced Language model
    return {**state, "messages": formatted_prompt}


def handle_compilation_error(state: RAGState):
    """
    Compilation error handler
    ### Input fields
        compilation_result (dict): The result of the compilation.
            {
                "valid": bool,
                "messages": List[str] # Processed compilation messages
            }
        compilation_attempts (int): Number of compilation attempts.
        messages (List[BaseMessage]): Agent message history.
        raw_completion (AIMessage): The raw completion from the coder.
    ### Fields modified
        messages (List[str]): Agent message history.
    """
    assert "compilation_result" in state, "State missing required key 'compilation_result'"
    assert "compilation_attempts" in state, "State missing required key 'compilation_attempts'"
    assert "messages" in state, "State missing required key 'messages'"
    assert "raw_completion" in state, "State missing required key 'raw_completion'"
    assert state["compilation_result"]["valid"] is False, "Compilation result must be invalid"

    # 1. Add the coder's completion (raw output) to the message history
    state["messages"].append(state["raw_completion"])
    # 2. Prepare the compilation error message and add it to the message history
    compilation_error_message = "\n".join(
        state["compilation_result"]["messages"])

    compilation_attempts = state["compilation_attempts"]

    # 3. Create a formatted system message for the error and attempts
    error_message = SystemMessagePromptTemplate.from_template(
        "Your completion failed to compile.\n"
        "Error: {error_message}\n"
        "This was attempt {compilation_attempts}.")

    error_message = error_message.format_messages(
        error_message=compilation_error_message,
        compilation_attempts=compilation_attempts
    )

    # Add this formatted error message to the history
    state["messages"].append(error_message[0])
    return state


def handle_judge_error(state: RAGState):
    """
    Judge error handler
    ### Input fields
        judgment (str)
        judge_output (str)
        judge_attempts (int): Number of judge attempts.
        messages (List[str]): Agent message history.
    ### Fields modified
        messages (List[str])
    """
    assert "judgment" in state, "State missing required key 'judgment'"
    assert "judge_attempts" in state, "State missing required key 'judge_attempts'"
    assert state["judgment"] in ['correct', 'incorrect', 'internal judgment error'], \
        "Judgment must be one of 'correct', 'incorrect', or 'internal judgment error"

    # 1. Prepare the judgment error message and add it to the message history
    judgment_error_message = state["judge_output"]
    judge_attempts = state["judge_attempts"]

    # 2. Create a formatted system message for the error and attempts
    error_message_template = SystemMessagePromptTemplate.from_template(
        "Your completion was rejected by the judge.\n"
        "Error: {error_message}\n"
        "This was attempt {judge_attempts}.")

    error_message = error_message_template.format_messages(
        error_message=judgment_error_message,
        judge_attempts=judge_attempts
    )

    # 3. Add this formatted error message to the history
    state["messages"].append(error_message[0])
    return state
