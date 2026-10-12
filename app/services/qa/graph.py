# from __future__ import annotations
# from typing import TypedDict
# from langgraph.graph import StateGraph, END
# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from langchain_groq import ChatGroq
# from app.core.config import get_settings
# from app.services.qa.prompts import SYSTEM_PROMPT, REWRITE_PROMPT
# from app.services.qa.retriever import HybridRetriever, RetrievedChunk
# from app.services.qa.corrective_rag import build_context, basic_groundedness_heuristic
# settings = get_settings()
# class GraphState(TypedDict, total=False):
#     question: str; rewritten_question: str; document_id: str; conversation_history: list[dict]; retrieved_chunks: list[RetrievedChunk]; draft_answer: str; answer: str; confidence: float; answer_type: str; retry: bool; db: object

# def get_llm() -> ChatGroq: return ChatGroq(api_key=settings.groq_api_key, model=settings.groq_model, temperature=0)

# def rewrite_query_node(state: GraphState) -> GraphState:
#     history = state.get("conversation_history", []); question = state["question"]
#     if not history: state["rewritten_question"] = question; return state
#     llm = get_llm(); messages = [SystemMessage(content=REWRITE_PROMPT)]
#     for m in history[-6:]: messages.append(HumanMessage(content=m["content"])) if m["role"] == "user" else messages.append(AIMessage(content=m["content"]))
#     messages.append(HumanMessage(content=f"User question: {question}"))
#     state["rewritten_question"] = llm.invoke(messages).content.strip() or question; return state

# def retrieve_node(state: GraphState) -> GraphState:
#     state["retrieved_chunks"] = HybridRetriever(db=state["db"], document_id=state["document_id"], top_k=settings.top_k).retrieve(state.get("rewritten_question") or state["question"])
#     return state

# def draft_answer_node(state: GraphState) -> GraphState:
#     llm = get_llm(); context = build_context(state.get("retrieved_chunks", [])); question = state.get("rewritten_question") or state["question"]
#     prompt = f"Question: {question}

# Context:
# {context}

# Answer in JSON with keys answer, grounded, confidence, cited_chunk_ids. If unsupported, say you could not find it in the document."
#     state["draft_answer"] = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]).content; return state

# def critique_node(state: GraphState) -> GraphState:
#     decision = basic_groundedness_heuristic(state.get("draft_answer", ""), state.get("retrieved_chunks", [])); state["confidence"] = decision.confidence
#     if decision.supported: state["answer_type"] = "grounded"; state["answer"] = state.get("draft_answer", ""); return state
#     if not state.get("retry"):
#         state["retry"] = True; context_hint = " ".join([c.text[:120] for c in state.get("retrieved_chunks", [])[:3]])
#         state["rewritten_question"] = f"{state.get('rewritten_question') or state['question']} {context_hint}"; return state
#     state["answer_type"] = "not_found"; state["answer"] = "I could not find this information in the uploaded document."; state["confidence"] = max(0.05, state.get("confidence", 0.0)); return state

# def build_graph():
#     graph = StateGraph(GraphState)
#     graph.add_node("rewrite", rewrite_query_node); graph.add_node("retrieve", retrieve_node); graph.add_node("draft", draft_answer_node); graph.add_node("critique", critique_node)
#     graph.set_entry_point("rewrite"); graph.add_edge("rewrite", "retrieve"); graph.add_edge("retrieve", "draft"); graph.add_edge("draft", "critique")
#     graph.add_conditional_edges("critique", lambda s: "retrieve" if s.get("retry") and s.get("answer_type") != "not_found" else END, {"retrieve": "retrieve", END: END})
#     return graph.compile()



from __future__ import annotations

from typing import TypedDict

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_groq import ChatGroq
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph

from app.core.config import get_settings
from app.services.qa.corrective_rag import (
    basic_groundedness_heuristic,
    build_context,
)
from app.services.qa.prompts import (
    REWRITE_PROMPT,
    SYSTEM_PROMPT,
)
from app.services.qa.retriever import (
    HybridRetriever,
    RetrievedChunk,
)

settings = get_settings()


class GraphState(TypedDict, total=False):
    question: str
    rewritten_question: str
    document_id: str
    conversation_history: list[dict]
    retrieved_chunks: list[RetrievedChunk]
    draft_answer: str
    answer: str
    confidence: float
    answer_type: str
    retry: bool
    db: object


def get_llm() -> ChatGroq:
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0,
    )


def rewrite_query_node(state: GraphState) -> GraphState:
    history = state.get("conversation_history", [])
    question = state["question"]

    # no history → no rewrite
    if not history:
        state["rewritten_question"] = question
        return state

    llm = get_llm()

    messages = [
        SystemMessage(content=REWRITE_PROMPT)
    ]

    for msg in history[-6:]:
        if msg["role"] == "user":
            messages.append(
                HumanMessage(content=msg["content"])
            )
        else:
            messages.append(
                AIMessage(content=msg["content"])
            )

    messages.append(
        HumanMessage(
            content=f"User question: {question}"
        )
    )

    response = llm.invoke(messages)

    rewritten = response.content.strip()

    state["rewritten_question"] = (
        rewritten if rewritten else question
    )

    return state


def retrieve_node(state: GraphState) -> GraphState:
    retriever = HybridRetriever(
        db=state["db"],
        document_id=state["document_id"],
        top_k=settings.top_k,
    )

    query = (
        state.get("rewritten_question")
        or state["question"]
    )

    chunks = retriever.retrieve(query)

    state["retrieved_chunks"] = chunks

    return state


def draft_answer_node(state: GraphState) -> GraphState:
    llm = get_llm()

    question = (
        state.get("rewritten_question")
        or state["question"]
    )

    retrieved_chunks = state.get(
        "retrieved_chunks",
        [],
    )

    context = build_context(retrieved_chunks)

    prompt = f"""
Question:
{question}

Context:
{context}

Instructions:
- Answer ONLY using the provided context.
- Do NOT hallucinate.
- If the answer is not found in the context,
  respond with:
  "I could not find this information in the uploaded document."

Return valid JSON with:
- answer
- grounded
- confidence
- cited_chunk_ids
"""

    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    state["draft_answer"] = response.content

    return state


def critique_node(state: GraphState) -> GraphState:
    draft_answer = state.get(
        "draft_answer",
        "",
    )

    retrieved_chunks = state.get(
        "retrieved_chunks",
        [],
    )

    decision = basic_groundedness_heuristic(
        draft_answer,
        retrieved_chunks,
    )

    state["confidence"] = decision.confidence

    # grounded answer
    if decision.supported:
        state["answer_type"] = "grounded"
        state["answer"] = draft_answer
        return state

    # retry once using retrieval hinting
    if not state.get("retry"):
        state["retry"] = True

        context_hint = " ".join(
            [
                c.text[:120]
                for c in retrieved_chunks[:3]
            ]
        )

        state["rewritten_question"] = (
            f"{state.get('rewritten_question') or state['question']} "
            f"{context_hint}"
        )

        return state

    # still unsupported
    state["answer_type"] = "not_found"

    state["answer"] = (
        "I could not find this information "
        "in the uploaded document."
    )

    state["confidence"] = max(
        0.05,
        state.get("confidence", 0.0),
    )

    return state


def should_retry(state: GraphState):
    if (
        state.get("retry")
        and state.get("answer_type") != "not_found"
    ):
        return "retrieve"

    return END


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node(
        "rewrite",
        rewrite_query_node,
    )

    graph.add_node(
        "retrieve",
        retrieve_node,
    )

    graph.add_node(
        "draft",
        draft_answer_node,
    )

    graph.add_node(
        "critique",
        critique_node,
    )

    graph.set_entry_point("rewrite")

    graph.add_edge(
        "rewrite",
        "retrieve",
    )

    graph.add_edge(
        "retrieve",
        "draft",
    )

    graph.add_edge(
        "draft",
        "critique",
    )

    graph.add_conditional_edges(
        "critique",
        should_retry,
        {
            "retrieve": "retrieve",
            END: END,
        },
    )

    return graph.compile()