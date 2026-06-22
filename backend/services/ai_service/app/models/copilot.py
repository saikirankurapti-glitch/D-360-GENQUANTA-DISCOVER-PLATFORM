import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

def naive_utcnow():
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    __table_args__ = {"schema": "ai"}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=naive_utcnow)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = {"schema": "ai"}

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("ai.chat_sessions.id"), nullable=False)
    role = Column(String(50), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=True)  # JSON representation of source citations
    created_at = Column(DateTime, default=naive_utcnow)

    session = relationship("ChatSession", back_populates="messages")
