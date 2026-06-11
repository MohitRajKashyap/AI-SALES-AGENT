"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('avatar_url', sa.String(512), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('role', sa.String(20), default='member'),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('logo_url', sa.String(512), nullable=True),
        sa.Column('website', sa.String(512), nullable=True),
        sa.Column('industry', sa.String(255), nullable=True),
        sa.Column('owner_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'workspace_members',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workspace_id', sa.String(36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('role', sa.String(20), default='member'),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.UniqueConstraint('workspace_id', 'user_id', name='uq_workspace_members_workspace_id_user_id'),
    )

    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True, unique=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True, unique=True),
        sa.Column('plan', sa.String(20), default='free'),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'companies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workspace_id', sa.String(36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('website_url', sa.String(512), nullable=False),
        sa.Column('company_name', sa.String(255), nullable=True),
        sa.Column('industry', sa.String(255), nullable=True),
        sa.Column('services', sa.JSON(), nullable=True),
        sa.Column('products', sa.JSON(), nullable=True),
        sa.Column('target_customers', sa.JSON(), nullable=True),
        sa.Column('pain_points', sa.JSON(), nullable=True),
        sa.Column('raw_content', sa.Text(), nullable=True),
        sa.Column('qdrant_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'leads',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workspace_id', sa.String(36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('companies.id'), nullable=True),
        sa.Column('company_name', sa.String(255), nullable=False),
        sa.Column('website', sa.String(512), nullable=True),
        sa.Column('industry', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('linkedin', sa.String(512), nullable=True),
        sa.Column('first_name', sa.String(255), nullable=True),
        sa.Column('last_name', sa.String(255), nullable=True),
        sa.Column('job_title', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('lead_score', sa.Integer(), default=0),
        sa.Column('status', sa.String(20), default='cold'),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('qdrant_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'campaigns',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workspace_id', sa.String(36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('goal', sa.Text(), nullable=True),
        sa.Column('daily_limit', sa.Integer(), default=50),
        sa.Column('email_style', sa.String(20), default='professional'),
        sa.Column('followup_days', sa.JSON(), nullable=True),
        sa.Column('target_industry', sa.String(255), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'emails',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id'), nullable=True),
        sa.Column('lead_id', sa.String(36), sa.ForeignKey('leads.id'), nullable=False),
        sa.Column('subject', sa.String(512), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('email_type', sa.String(30), default='cold'),
        sa.Column('email_style', sa.String(20), default='professional'),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('opened_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('replied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('followup_day', sa.Integer(), nullable=True),
        sa.Column('tracking_id', sa.String(36), nullable=False, unique=True),
        sa.Column('qdrant_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'analytics',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workspace_id', sa.String(36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('emails_sent', sa.Integer(), default=0),
        sa.Column('emails_opened', sa.Integer(), default=0),
        sa.Column('replies', sa.Integer(), default=0),
        sa.Column('meetings_booked', sa.Integer(), default=0),
        sa.Column('new_leads', sa.Integer(), default=0),
        sa.Column('conversions', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'agent_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workspace_id', sa.String(36), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('agent_type', sa.String(30), nullable=False),
        sa.Column('status', sa.String(20), default='running'),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), default=0),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('agent_logs')
    op.drop_table('analytics')
    op.drop_table('emails')
    op.drop_table('campaigns')
    op.drop_table('leads')
    op.drop_table('companies')
    op.drop_table('subscriptions')
    op.drop_table('workspace_members')
    op.drop_table('workspaces')
    op.drop_table('users')
