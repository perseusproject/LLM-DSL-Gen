# -* coding: utf-8 *-
# dsl_gen/core/rag.py


import logging
from ..config import CFG

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage
from langchain_core.prompts import (ChatPromptTemplate,
                                    SystemMessagePromptTemplate,
                                    HumanMessagePromptTemplate)

from typing import Any, List, Optional, TypedDict, Literal, Dict
from .vector_store import get_vectorstore

logger = logging.getLogger('dsl_gen')


class RAGState(TypedDict):
    # Input
    challenge_path: Optional[str]  # Path to the challenge json file
    question: Optional[str]  # Question to be answered
    question_type: Optional[Literal["QA", "coding"]]  # Question type

    # For evaluation mode
    ground_truth: Optional[str]  # Ground truth answer
    ref: Optional[str]  # Reference answer

    # Retrieved documents
    docs: Optional[List[Document]]

    # Input to the coder
    messages: Optional[List[BaseMessage]]

    # Output from the coder
    raw_completion: Optional[AIMessage]
    completion: Optional[str]  # The last completion

    # Output from the compiler
    # compilation_result = {
    #     "valid": bool,
    #     "messages": List[str]
    # }
    compilation_result: Optional[Dict[str, Any]]
    compilation_attempts: int

    # Output from the judge
    # Either 'correct', 'incorrect' or 'internal judgment error'
    judgment: Optional[str]
    judge_output: Optional[str]
    judgment_attempts: int


# Retrieve Docs Node

def _retrieve_docs(query: str, top_k: int = None) -> List[Document]:
    """Enhanced retrieval function"""

    top_k = top_k or CFG.EMBEDDING_CFG.top_k

    try:
        vectorstore = get_vectorstore()
        # Example of a hybrid retrieval strategy: filtering based on metadata
        # TODO: Implement a more sophisticated filtering strategy
        # TODO: Add references to the RAG flow for better completion results
        return vectorstore.similarity_search(
            query,
            k=top_k
            # ,filter={
            #     "source": "official_docs"  # Assuming documents have a source metadata field
            # }
        )
    except Exception as e:
        logger.error(f"Retrieval failed: {str(e)}")
        return []


def retrieve_docs(state: RAGState) -> RAGState:
    """Document retrieval node
    ### Input fields
        question (str): The question to be answered.
        question_type (str): The type of question (QA or coding) # Not really used
    ### Fields added
        docs (List[Document]): The retrieved documents.
    """
    # Input fields: question, question_type
    # Output fields: docs

    # Defensive programming is IMPORTANT!!!
    assert "question" in state, "Question must be provided in the state"

    query = state["question"]
    logger.debug(f"Retrieving docs for query: {query}")

    docs = _retrieve_docs(query)
    logger.info(f"Retrieved {len(docs)} docs")
    return {**state, "docs": docs}

# Generate Prompt Node


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
    assert ("question" in state) and (
        state["question"] is not None), "Question must be provided in the state"
    assert ("question_type" in state) and (
        state["question_type"] is not None), "Question type must be provided in the state"
    assert ("docs" in state) and (
        state["docs"] is not None), "Retrieved documents must be provided in the state"

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


__all__ = ["retrieve_docs", "generate_prompt"]
