# -* coding: utf-8 *-
# dsl_gen/core/rag.py


import logging
import json
from ..config import CFG

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.prompts import (ChatPromptTemplate,
                                    SystemMessagePromptTemplate,
                                    HumanMessagePromptTemplate)

from typing import Any, List, Optional, TypedDict, Literal
from .vector_store import get_vectorstore

logger = logging.getLogger('dsl_gen')

PATH_CFG = CFG.PATH_CFG
MODEL_CFG = CFG.MODEL_CFG
EMBEDDING_CFG = CFG.EMBEDDING_CFG


class RAGState(TypedDict):
    challenge_path: Optional[str]
    question: Optional[str]
    question_type: Optional[Literal["QA", "code"]]

    answer: Optional[str]
    ref: Optional[str]
    eval: Optional[bool]

    docs: Optional[List[Document]]
    messages: Optional[List[BaseMessage]]

    compiled: Optional[Any]
    error: Optional[str]
    judgment: Optional[str]

# QA Splitter Node


def qa_splitter(state: RAGState) -> RAGState:
    # 　either question or challenge_path should be provided
    assert ("question" in state) != ("challenge_path" in state)

    if state.get("question"):
        logger.debug("QA Splitter: question provided, eval mode")

        return {**state, "eval": True}

    elif state.get("challenge_path"):
        logger.debug("QA Splitter: challenge path provided")

        # read the challenge path json file
        with open(state["challenge_path"]) as f:
            challenge = json.load(f)
        return {**state,
                "eval": False,
                "question": challenge["question"],
                "answer": challenge["answer"],
                "ref": challenge["ref"],
                "question_type": challenge["type"]}


# Retrieve Docs Node
def _retrieve_docs(query: str, top_k: int = EMBEDDING_CFG.top_k) -> List[Document]:
    """Enhanced retrieval function"""
    try:
        vectorstore = get_vectorstore()
        # Example of a hybrid retrieval strategy: filtering based on metadata
        return vectorstore.similarity_search(
            query,
            k=top_k,
            filter={
                "source": "official_docs"  # Assuming documents have a source metadata field
            }
        )
    except Exception as e:
        logger.error(f"Retrieval failed: {str(e)}")
        return []


def retrieve_docs(state: RAGState) -> RAGState:
    """Enhanced retrieval node"""
    query = state["question"]
    docs = _retrieve_docs(query)
    logger.info(f"Retrieved {len(docs)} docs for query: {query}")
    return {**state, "docs": docs}

# Generate Prompt Node


def _format_context(docs: List[Document]) -> str:
    """Format the retrieved documents into a context string"""
    return "\n\n".join(
        f"Document {i+1} (from {doc.metadata.get('source', 'unknown')}):\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )


def generate_prompt(state: RAGState) -> RAGState:
    """Construct an enhanced prompt using LangChain native templates"""
    # Create a hierarchical prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=CFG.MODEL_CFG.CODER.personality),
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

    # Changed to messages to be compatible with LCEL
    # LangChain Enhanced Language model
    return {**state, "messages": formatted_prompt}
