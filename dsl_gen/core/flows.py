# dsl_gen/core/flows.py
from langgraph.graph import StateGraph, END
from dsl_gen.core.rag import RAGState, qa_splitter, retrieve_docs, generate_prompt
from dsl_gen.agents.llm_coder import generate_answer
from dsl_gen.agents.lokad_compiler import compile_code
from dsl_gen.agents.llm_judge import judge_answer

def build_rag_flow():
    workflow = StateGraph(RAGState)
    workflow.add_node("QA_splitter", qa_splitter)
    workflow.add_node("retriever", retrieve_docs)
    workflow.add_node("prompt_generator",generate_prompt)
    workflow.add_node("llm_coder", generate_answer)
    workflow.add_node("compiler", compile_code)
    workflow.add_node("judge", judge_answer)

    workflow.set_entry_point("QA_splitter")
    workflow.add_edge("QA_splitter", "retriever")
    workflow.add_edge("retriever", "prompt_generator")
    workflow.add_edge("prompt_generator", "llm_coder")
    workflow.add_edge("llm_coder", "compiler")

    def handle_compilation(state: RAGState):
        return "prompt_generator" if state.get("error") else "judge"

    workflow.add_conditional_edges(
        "compiler",
        handle_compilation,
        {"prompt_generator": "prompt_generator", "judge": "judge"}
    )
    
    def handle_judgment(state: RAGState):
        return END if state.get("judgment") == "correct" else "prompt_generator"

    workflow.add_conditional_edges(
        "judge",
        handle_judgment,
        {"prompt_generator": "prompt_generator", END: END}
    )

    return workflow.compile()