# -* coding: utf-8 *-
# dsl_gen/core/flows.py
import json
from langgraph.graph import StateGraph, END
from dsl_gen.core.rag import RAGState, retrieve_docs, generate_prompt
from dsl_gen.agents.llm_coder import llm_coder
from dsl_gen.agents.lokad_compiler import compile_code, handle_compilation
from dsl_gen.agents.llm_judge import judge_answer, handle_judgment
import logging
import re


logger = logging.getLogger('dsl_gen')


def qa_splitter(state: RAGState) -> RAGState:
    """QA Splitter node"""
    # 　either question or challenge_path should be provided
    assert ("question" in state) != ("challenge_path" in state)

    if state.get("question"):
        logger.debug("QA Splitter: question provided, eval mode")

        return {**state, "eval": True}

    elif state.get("challenge_path"):
        logger.debug("QA Splitter: challenge path provided, path=%s",
                     state["challenge_path"])

        # read the challenge path json file
        with open(state["challenge_path"]) as f:
            challenge = json.load(f)
        return {**state,
                "eval": False,
                "question": challenge["question"],
                "ground_truth": challenge["answer"],
                "ref": challenge["ref"],
                "question_type": challenge["type"]}


def completion_peeler(state: RAGState) -> RAGState:
    """Answer peeler node"""
    if "completion" not in state:
        logger.error("State missing required key 'completion'")
        raise ValueError("Input state must contain 'completion' key")

    completion_content = state["completion"]["content"]
    # Remove <think>...</think> tags
    completion_content = re.sub(r'<think[\s\S]*?>[\s\S]*?</think>',
                                '', completion_content, flags=re.DOTALL)

    try:
        import IPython
        from IPython.display import display, Markdown
        if IPython.get_ipython() is None:
            raise ImportError
        display(Markdown("### Question"))
        display(Markdown(state["question"]))
        display(Markdown("### Coder's Completion"))
        display(Markdown(completion_content))
    except ImportError:
        print("### Question")
        print(state["question"])
        print("### Coder's Completion")
        print(completion_content)
        pass

    # Match code blocks enclosed in triple backticks or ```envision...```
    if state["question_type"] == "coding":
        code_blocks = re.findall(
            r'```(?:envision)?\s*\n?(.*?)\n?```', completion_content, flags=re.DOTALL)

        if not code_blocks:
            logger.warning("No valid code blocks found in completion")
            return {**state, "completion": completion_content}

        # Get the first code block
        extracted_code = code_blocks[0].strip()
        return {**state, "completion": extracted_code}
    else:
        return {**state, "completion": completion_content}


def build_rag_flow():
    workflow = StateGraph(RAGState)
    # Preprocessor
    workflow.add_node("QA_splitter", qa_splitter)
    # RAG
    workflow.add_node("retriever", retrieve_docs)
    workflow.add_node("prompt_generator", generate_prompt)
    # Coder
    workflow.add_node("llm_coder", llm_coder)
    workflow.add_node("completion_peeler", completion_peeler)
    # Compiler
    workflow.add_node("compiler", compile_code)
    # Judge
    workflow.add_node("judge", judge_answer)

    workflow.set_entry_point("QA_splitter")
    workflow.add_edge("QA_splitter", "retriever")
    workflow.add_edge("retriever", "prompt_generator")
    workflow.add_edge("prompt_generator", "llm_coder")
    workflow.add_edge("llm_coder", "completion_peeler")
    workflow.add_edge("completion_peeler", "compiler")

    workflow.add_edge("compiler", END)
    workflow.add_conditional_edges(
        "compiler",
        handle_compilation,
        {
            "llm_coder": "llm_coder",
            "judge": "judge",
            END: END
        }
    )

    workflow.add_conditional_edges(
        "judge",
        handle_judgment,
        {
            "prompt_generator": "prompt_generator",
            END: END
        }
    )

    return workflow.compile()
