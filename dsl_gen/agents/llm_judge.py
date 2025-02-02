# dsl_gen/backend/llm_judge.py
from .api import getClient
from dsl_gen.core.rag import RAGState

def _judge_answer(answer: str, question: str):
    client = getClient()
    response = client.invoke(question, answer)
    return response.model_dump()

def judge_answer(state: RAGState):
    return {**state, "judgment": _judge_answer(state["answer"], state["question"])}
