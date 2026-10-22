"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-05-11
"""
from alembic import op
import sqlalchemy as sa
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("documents", sa.Column("id", sa.String(length=36), primary_key=True), sa.Column("filename", sa.String(length=255), nullable=False), sa.Column("file_type", sa.String(length=32), nullable=False), sa.Column("storage_path", sa.String(length=512), nullable=False), sa.Column("status", sa.Enum("PENDING", "PROCESSING", "READY", "FAILED", name="documentstatus"), nullable=False), sa.Column("progress", sa.Integer(), nullable=False, server_default="0"), sa.Column("error_message", sa.Text(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))
    op.create_table("document_chunks", sa.Column("id", sa.String(length=36), primary_key=True), sa.Column("document_id", sa.String(length=36), sa.ForeignKey("documents.id", ondelete="CASCADE")), sa.Column("chunk_index", sa.Integer(), nullable=False), sa.Column("page_number", sa.Integer(), nullable=True), sa.Column("chunk_text", sa.Text(), nullable=False), sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"), sa.Column("dense_score", sa.Float(), nullable=True), sa.Column("sparse_score", sa.Float(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])
    op.create_table("conversations", sa.Column("id", sa.String(length=36), primary_key=True), sa.Column("document_id", sa.String(length=36), sa.ForeignKey("documents.id", ondelete="CASCADE")), sa.Column("title", sa.String(length=255), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))
    op.create_index("ix_conversations_document_id", "conversations", ["document_id"])
    op.create_table("messages", sa.Column("id", sa.String(length=36), primary_key=True), sa.Column("conversation_id", sa.String(length=36), sa.ForeignKey("conversations.id", ondelete="CASCADE")), sa.Column("role", sa.Enum("user", "assistant", name="messagerole"), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    op.create_table("ingestion_jobs", sa.Column("id", sa.String(length=36), primary_key=True), sa.Column("document_id", sa.String(length=36), nullable=False), sa.Column("job_status", sa.String(length=32), nullable=False), sa.Column("started_at", sa.DateTime(timezone=True), nullable=True), sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True), sa.Column("error_message", sa.Text(), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))
    op.create_index("ix_ingestion_jobs_document_id", "ingestion_jobs", ["document_id"])

def downgrade():
    op.drop_table("ingestion_jobs")
    op.drop_index("ix_messages_conversation_id", table_name="messages")
    op.drop_table("messages")
    op.drop_index("ix_conversations_document_id", table_name="conversations")
    op.drop_table("conversations")
    op.drop_index("ix_document_chunks_document_id", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_table("documents")
