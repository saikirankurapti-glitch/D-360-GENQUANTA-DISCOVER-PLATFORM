import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

def naive_utcnow():
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)

class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"
    __table_args__ = {"schema": "workflow"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    nodes_json = Column(Text, nullable=False)  # JSON representation of React Flow nodes
    edges_json = Column(Text, nullable=False)  # JSON representation of React Flow edges
    trigger_type = Column(String(50), default="MANUAL")  # MANUAL, SCHEDULED, EVENT
    cron_schedule = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=naive_utcnow)
    updated_at = Column(DateTime, default=naive_utcnow, onupdate=naive_utcnow)

    runs = relationship("WorkflowRun", back_populates="definition", cascade="all, delete-orphan")

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"
    __table_args__ = {"schema": "workflow"}

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflow.workflow_definitions.id"), nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED, WAITING_APPROVAL
    started_at = Column(DateTime, default=naive_utcnow)
    finished_at = Column(DateTime, nullable=True)
    current_step_idx = Column(Integer, default=0)
    logs = Column(Text, nullable=True)

    definition = relationship("WorkflowDefinition", back_populates="runs")
    steps = relationship("WorkflowStep", back_populates="run", cascade="all, delete-orphan")
    approvals = relationship("WorkflowApproval", back_populates="run", cascade="all, delete-orphan")

class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    __table_args__ = {"schema": "workflow"}

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("workflow.workflow_runs.id"), nullable=False)
    step_id = Column(String(50), nullable=False)  # React Flow node ID
    step_name = Column(String(100), nullable=False)
    node_type = Column(String(50), nullable=False)  # datasource, sync, query, compound_search, sequence_analysis, assay_analysis, export, notification, approval
    status = Column(String(50), default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED, WAITING
    inputs_json = Column(Text, nullable=True)
    outputs_json = Column(Text, nullable=True)
    logs = Column(Text, nullable=True)
    execution_time_ms = Column(Float, default=0.0)

    run = relationship("WorkflowRun", back_populates="steps")

class WorkflowSchedule(Base):
    __tablename__ = "workflow_schedules"
    __table_args__ = {"schema": "workflow"}

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, nullable=False)
    cron_expression = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)

class WorkflowEvent(Base):
    __tablename__ = "workflow_events"
    __table_args__ = {"schema": "workflow"}

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)  # new_file, new_assay_data, new_eln_record, new_lims_record
    payload_json = Column(Text, nullable=False)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=naive_utcnow)

class WorkflowApproval(Base):
    __tablename__ = "workflow_approvals"
    __table_args__ = {"schema": "workflow"}

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("workflow.workflow_runs.id"), nullable=False)
    step_id = Column(String(50), nullable=False)  # React Flow node ID of approval step
    role_required = Column(String(50), nullable=False)  # SCIENTIST, REVIEWER, COMPLIANCE
    status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED
    requested_at = Column(DateTime, default=naive_utcnow)
    completed_at = Column(DateTime, nullable=True)
    approved_by = Column(String(100), nullable=True)
    signature_hash = Column(String(256), nullable=True)
    comment = Column(Text, nullable=True)

    run = relationship("WorkflowRun", back_populates="approvals")
