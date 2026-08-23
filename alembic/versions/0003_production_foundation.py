"""Add ownership, integrity, document storage, and discovery deduplication."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0003_production_foundation"
down_revision = "0002_auth_rag"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("candidates", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("jobs", sa.Column("dedupe_key", sa.String(64), nullable=True))
    op.execute("UPDATE jobs SET dedupe_key = md5(coalesce(company, '') || '|' || coalesce(title, '') || '|' || coalesce(application_url, ''))")
    op.create_foreign_key("fk_candidates_user", "candidates", "users", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key("fk_candidate_chunks_candidate", "candidate_chunks", "candidates", ["candidate_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key("fk_applications_candidate", "applications", "candidates", ["candidate_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key("fk_applications_job", "applications", "jobs", ["job_id"], ["id"], ondelete="RESTRICT")
    op.create_index("ix_candidates_user_id", "candidates", ["user_id"])
    op.create_index("ix_jobs_dedupe_key", "jobs", ["dedupe_key"])
    op.create_index("ix_applications_candidate_status", "applications", ["candidate_id", "status"])
    op.create_unique_constraint("uq_jobs_dedupe_key", "jobs", ["dedupe_key"])
    op.create_table("documents", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False), sa.Column("storage_key", sa.String(128), nullable=False, unique=True), sa.Column("sha256", sa.String(64), nullable=False), sa.Column("content_type", sa.String(120), nullable=False), sa.Column("size_bytes", sa.Integer, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_index("ix_documents_candidate_id", "documents", ["candidate_id"])
    op.create_index("ix_documents_sha256", "documents", ["sha256"])
    op.alter_column("candidates", "user_id", nullable=False)
    op.alter_column("jobs", "dedupe_key", nullable=False)


def downgrade() -> None:
    op.drop_table("documents")
    op.drop_constraint("uq_jobs_dedupe_key", "jobs", type_="unique")
    op.drop_index("ix_applications_candidate_status", table_name="applications")
    op.drop_index("ix_jobs_dedupe_key", table_name="jobs")
    op.drop_index("ix_candidates_user_id", table_name="candidates")
    op.drop_constraint("fk_applications_job", "applications", type_="foreignkey")
    op.drop_constraint("fk_applications_candidate", "applications", type_="foreignkey")
    op.drop_constraint("fk_candidate_chunks_candidate", "candidate_chunks", type_="foreignkey")
    op.drop_constraint("fk_candidates_user", "candidates", type_="foreignkey")
    op.drop_column("jobs", "dedupe_key")
    op.drop_column("candidates", "user_id")
