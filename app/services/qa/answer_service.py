# from __future__ import annotations
# from sqlalchemy.orm import Session
# from app.db.models.conversation import Conversation
# from app.db.models.message import Message, MessageRole
# from app.schemas.qa import AskResponse, SourceChunk
# from app.services.qa.graph import build_graph

# def load_conversation_history(db: Session, conversation_id: str | None) -> list[dict]:
#     if not conversation_id: return []
#     msgs = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
#     return [{"role": m.role.value, "content": m.content} for m in msgs]

# def ensure_conversation(db: Session, document_id: str, conversation_id: str | None) -> Conversation:
#     if conversation_id:
#         convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
#         if convo: return convo
#     convo = Conversation(document_id=document_id, title=None); db.add(convo); db.commit(); db.refresh(convo); return convo

# def ask_question(db: Session, document_id: str, question: str, conversation_id: str | None = None) -> AskResponse:
#     convo = ensure_conversation(db, document_id, conversation_id)
#     db.add(Message(conversation_id=convo.id, role=MessageRole.USER, content=question)); db.commit()
#     result = build_graph().invoke({"document_id": document_id, "question": question, "conversation_history": load_conversation_history(db, convo.id), "db": db, "retry": False})
#     answer = result.get("answer", "I could not find this information in the uploaded document."); confidence = float(result.get("confidence", 0.0)); answer_type = result.get("answer_type", "grounded")
#     db.add(Message(conversation_id=convo.id, role=MessageRole.ASSISTANT, content=answer)); db.commit()
#     sources = [SourceChunk(chunk_id=c.chunk_id, page_number=c.page_number, score=float(c.hybrid_score), text=c.text) for c in result.get("retrieved_chunks", [])[:6]]
#     return AskResponse(answer=answer, document_id=document_id, conversation_id=convo.id, answer_type=answer_type, confidence=confidence, sources=sources)




from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.conversation import Conversation
from app.db.models.message import (
    Message,
    MessageRole,
)
from app.schemas.qa import (
    AskResponse,
    SourceChunk,
)
from app.services.qa.graph import build_graph


def load_conversation_history(
    db: Session,
    conversation_id: str | None,
) -> list[dict]:
    """
    Load ordered conversation history.
    """

    if not conversation_id:
        return []

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id
            == conversation_id
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    return [
        {
            "role": m.role.value,
            "content": m.content,
        }
        for m in messages
    ]


def ensure_conversation(
    db: Session,
    document_id: str,
    conversation_id: str | None,
) -> Conversation:
    """
    Reuse existing conversation if present.
    Otherwise create new conversation.
    """

    if conversation_id:
        convo = (
            db.query(Conversation)
            .filter(
                Conversation.id
                == conversation_id
            )
            .first()
        )

        if convo:
            return convo

    convo = Conversation(
        document_id=document_id,
        title=None,
    )

    db.add(convo)

    db.commit()

    db.refresh(convo)

    return convo


def ask_question(
    db: Session,
    document_id: str,
    question: str,
    conversation_id: str | None = None,
) -> AskResponse:
    """
    Main QA orchestration function.
    """

    convo = ensure_conversation(
        db,
        document_id,
        conversation_id,
    )

    # Save user message
    user_message = Message(
        conversation_id=convo.id,
        role=MessageRole.user,
        content=question,
    )

    db.add(user_message)

    db.commit()

    history = load_conversation_history(
        db,
        convo.id,
    )

    graph = build_graph()

    result = graph.invoke(
        {
            "document_id": document_id,
            "question": question,
            "conversation_history": history,
            "db": db,
            "retry": False,
        }
    )

    answer = result.get(
        "answer",
        "I could not find this information "
        "in the uploaded document.",
    )

    confidence = float(
        result.get("confidence", 0.0)
    )

    answer_type = result.get(
        "answer_type",
        "grounded",
    )

    # Save assistant message
    assistant_message = Message(
        conversation_id=convo.id,
        role=MessageRole.assistant,
        content=answer,
    )

    db.add(assistant_message)

    db.commit()

    retrieved_chunks = result.get(
        "retrieved_chunks",
        [],
    )

    sources = [
        SourceChunk(
            chunk_id=c.chunk_id,
            page_number=c.page_number,
            score=float(c.hybrid_score),
            text=c.text,
        )
        for c in retrieved_chunks[:6]
    ]

    return AskResponse(
        answer=answer,
        document_id=document_id,
        conversation_id=convo.id,
        answer_type=answer_type,
        confidence=confidence,
        sources=sources,
    )