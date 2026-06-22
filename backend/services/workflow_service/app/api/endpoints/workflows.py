import json
import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.workflow import WorkflowDefinition, WorkflowRun, WorkflowStep, WorkflowApproval, WorkflowEvent
from app.engine.executor import WorkflowExecutor

router = APIRouter(prefix="/workflows", tags=["workflows"])
executor = WorkflowExecutor()

# Pydantic Schemas
class WorkflowDefinitionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    nodes_json: str
    edges_json: str
    trigger_type: str = "MANUAL"
    cron_schedule: Optional[str] = None
    is_active: bool = True

class WorkflowDefinitionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    nodes_json: str
    edges_json: str
    trigger_type: str
    cron_schedule: Optional[str]
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class WorkflowRunResponse(BaseModel):
    id: int
    workflow_id: int
    status: str
    started_at: datetime.datetime
    finished_at: Optional[datetime.datetime]
    current_step_idx: int
    logs: Optional[str]

    class Config:
        from_attributes = True

class WorkflowStepResponse(BaseModel):
    id: int
    run_id: int
    step_id: str
    step_name: str
    node_type: str
    status: str
    inputs_json: Optional[str]
    outputs_json: Optional[str]
    logs: Optional[str]
    execution_time_ms: float

    class Config:
        from_attributes = True

class WorkflowApprovalResponse(BaseModel):
    id: int
    run_id: int
    step_id: str
    role_required: str
    status: str
    requested_at: datetime.datetime
    completed_at: Optional[datetime.datetime]
    approved_by: Optional[str]
    comment: Optional[str]

    class Config:
        from_attributes = True

class ApprovalActionRequest(BaseModel):
    status: str  # APPROVED, REJECTED
    approved_by: str
    comment: Optional[str] = None
    signature_payload: Optional[Dict[str, Any]] = None

class EventTriggerRequest(BaseModel):
    event_type: str
    payload: Dict[str, Any]


# ==========================================
# 1. Collection & Static Routes (First Priority)
# ==========================================

@router.post("", response_model=WorkflowDefinitionResponse, status_code=status.HTTP_201_CREATED)
def create_workflow_definition(obj_in: WorkflowDefinitionCreate, db: Session = Depends(get_db)):
    db_obj = WorkflowDefinition(
        name=obj_in.name,
        description=obj_in.description,
        nodes_json=obj_in.nodes_json,
        edges_json=obj_in.edges_json,
        trigger_type=obj_in.trigger_type,
        cron_schedule=obj_in.cron_schedule,
        is_active=obj_in.is_active
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("", response_model=List[WorkflowDefinitionResponse])
def get_workflow_definitions(db: Session = Depends(get_db)):
    return db.query(WorkflowDefinition).all()

@router.get("/runs", response_model=List[WorkflowRunResponse])
def get_workflow_runs(db: Session = Depends(get_db)):
    return db.query(WorkflowRun).order_by(WorkflowRun.started_at.desc()).all()

@router.get("/approvals", response_model=List[WorkflowApprovalResponse])
def get_approvals(db: Session = Depends(get_db)):
    return db.query(WorkflowApproval).order_by(WorkflowApproval.requested_at.desc()).all()

@router.post("/events/trigger")
def trigger_event(req: EventTriggerRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Create Event Record
    evt = WorkflowEvent(
        event_type=req.event_type,
        payload_json=json.dumps(req.payload),
        processed=False
    )
    db.add(evt)
    db.commit()
    db.refresh(evt)

    # Search for active workflow definitions matching this event trigger
    definitions = db.query(WorkflowDefinition).filter(
        WorkflowDefinition.trigger_type == "EVENT",
        WorkflowDefinition.is_active == True
    ).all()

    triggered_count = 0
    for definition in definitions:
        run = WorkflowRun(
            workflow_id=definition.id,
            status="PENDING",
            current_step_idx=0,
            logs=f"[{datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')}] Workflow triggered by event: {req.event_type}."
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        # Trigger execution in background
        background_tasks.add_task(executor.execute_run, run.id)
        triggered_count += 1

    evt.processed = True
    evt.processed_at = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    db.commit()

    return {"status": "success", "triggered_runs": triggered_count, "event_id": evt.id}


# ==========================================
# 2. Nested Sub-resource Routes
# ==========================================

@router.get("/runs/{run_id}", response_model=WorkflowRunResponse)
def get_workflow_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Workflow run not found.")
    return run

@router.get("/runs/{run_id}/steps", response_model=List[WorkflowStepResponse])
def get_workflow_run_steps(run_id: int, db: Session = Depends(get_db)):
    return db.query(WorkflowStep).filter(WorkflowStep.run_id == run_id).all()

@router.post("/approvals/{approval_id}/action")
async def approve_reject_workflow(
    approval_id: int,
    action: ApprovalActionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    approval = db.query(WorkflowApproval).filter(WorkflowApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found.")

    if approval.status != "PENDING":
        raise HTTPException(status_code=400, detail="Approval request has already been processed.")

    if action.status not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Invalid approval status action.")

    approval.status = action.status
    approval.approved_by = action.approved_by
    approval.completed_at = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    approval.comment = action.comment

    if action.status == "APPROVED":
        sig_data = action.signature_payload or {}
        import hashlib
        h = hashlib.sha256()
        h.update(f"{approval.run_id}-{approval.step_id}-{action.approved_by}-{approval.completed_at.isoformat()}".encode())
        approval.signature_hash = h.hexdigest()
        db.commit()

        # Resume execution in background
        background_tasks.add_task(executor.resume_run, approval.run_id, approval.id, sig_data)
    else:
        db.commit()
        run = db.query(WorkflowRun).filter(WorkflowRun.id == approval.run_id).first()
        if run:
            run.status = "FAILED"
            run.finished_at = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
            timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
            run.logs += f"\n[{timestamp}] Step '{approval.step_id}' rejected by compliance officer {action.approved_by}. Workflow aborted."
            db.commit()

            step = db.query(WorkflowStep).filter(
                WorkflowStep.run_id == run.id,
                WorkflowStep.step_id == approval.step_id
            ).first()
            if step:
                step.status = "FAILED"
                step.logs = f"Approval rejected: {action.comment}"
                db.commit()

    return {"status": "success", "message": f"Workflow run {approval.run_id} updated with action: {action.status}"}


# ==========================================
# 3. Wildcard Routes (Lowest Priority)
# ==========================================

@router.get("/{id}", response_model=WorkflowDefinitionResponse)
def get_workflow_definition(id: int, db: Session = Depends(get_db)):
    db_obj = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Workflow definition not found.")
    return db_obj

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_workflow_definition(id: int, db: Session = Depends(get_db)):
    db_obj = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Workflow definition not found.")
    db.delete(db_obj)
    db.commit()
    return {"message": "Workflow definition deleted successfully."}

@router.post("/{id}/run", response_model=WorkflowRunResponse)
def run_workflow(id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    definition = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == id).first()
    if not definition:
        raise HTTPException(status_code=404, detail="Workflow definition not found.")

    run = WorkflowRun(
        workflow_id=id,
        status="PENDING",
        current_step_idx=0,
        logs=f"[{datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')}] Workflow queued for execution."
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Queue background task execution
    background_tasks.add_task(executor.execute_run, run.id)
    return run
