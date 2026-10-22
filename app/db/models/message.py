# import enum, uuid
# from sqlalchemy import String, DateTime, Text, Enum, ForeignKey, func
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from app.db.base import Base
# class MessageRole(str, enum.Enum): USER = "user"; ASSISTANT = "assistant"
# class Message(Base):
#     __tablename__ = "messages"
#     id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
#     role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
#     content: Mapped[str] = mapped_column(Text, nullable=False)
#     created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
#     conversation = relationship("Conversation", back_populates="messages")



import enum
import uuid

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    role: Mapped[MessageRole] = mapped_column(
        Enum(
            MessageRole,
            values_callable=lambda obj: [
                e.value for e in obj
            ],
        ),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages",
    )