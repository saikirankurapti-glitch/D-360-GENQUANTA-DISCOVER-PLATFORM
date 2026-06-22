import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.copilot import ChatSession, ChatMessage
from app.services.chat_service import chat_service
from app.services.query_planner import query_planner
from app.services.analytics_service import analytics_service
from app.services.report_generator import report_generator
from app.services.dashboard_generator import dashboard_generator
from app.services.workflow_generator import workflow_generator
from app.core.compliance_client import log_audit_event

router = APIRouter()

# Pydantic Schemas
class ChatSessionCreate(BaseModel):
    title: str

class ChatMessageRequest(BaseModel):
    message: str

class QueryPlanRequest(BaseModel):
    query: str

class AnalyticsRequest(BaseModel):
    data_type: str  # alignment, clustering, assay, experiment
    payload: Dict[str, Any]

class ReportRequest(BaseModel):
    title: str
    format: str  # excel, pdf, ppt
    description: Optional[str] = "Generated scientific report"
    data: Optional[List[Dict[str, Any]]] = None
    slides: Optional[List[Dict[str, Any]]] = None

class DashboardRequest(BaseModel):
    prompt: str

class WorkflowRequest(BaseModel):
    prompt: str

# API Routes
@router.post("/chat/sessions")
def create_session(session_data: ChatSessionCreate, db: Session = Depends(get_db)):
    session = chat_service.create_session(session_data.title, db)
    log_audit_event(
        action="COPILOT_SESSION_CREATE",
        service_name="ai_service",
        username="Scientist",
        endpoint="/api/v1/copilot/chat/sessions",
        details={"session_id": session.id, "title": session.title}
    )
    return session

@router.get("/chat/sessions")
def get_sessions(db: Session = Depends(get_db)):
    return chat_service.get_sessions(db)

@router.get("/chat/sessions/{session_id}/messages")
def get_messages(session_id: int, db: Session = Depends(get_db)):
    return chat_service.get_messages(session_id, db)

@router.post("/chat/sessions/{session_id}/respond")
async def respond_to_message(session_id: int, req: ChatMessageRequest, db: Session = Depends(get_db)):
    msg = await chat_service.generate_response(session_id, req.message, db)
    
    # Audit log
    log_audit_event(
        action="COPILOT_CHAT_MESSAGE",
        service_name="ai_service",
        username="Scientist",
        endpoint=f"/api/v1/copilot/chat/sessions/{session_id}/respond",
        details={"session_id": session_id, "user_query": req.message, "citations_count": len(json.loads(msg.citations_json or "[]"))}
    )
    
    return msg

@router.post("/query-plan")
def create_query_plan(req: QueryPlanRequest):
    plan = query_planner.plan_query(req.query)
    
    # Audit log
    log_audit_event(
        action="COPILOT_QUERY_PLAN",
        service_name="ai_service",
        username="Scientist",
        endpoint="/api/v1/copilot/query-plan",
        details={"query": req.query, "sql": plan.get("generated_sql")}
    )
    
    return plan

@router.post("/analytics")
def get_scientific_insights(req: AnalyticsRequest):
    insights = analytics_service.analyze_results(req.data_type, req.payload)
    
    # Audit log
    log_audit_event(
        action="COPILOT_ANALYTICS_GEN",
        service_name="ai_service",
        username="Scientist",
        endpoint="/api/v1/copilot/analytics",
        details={"data_type": req.data_type}
    )
    
    return insights

@router.post("/report")
def export_report(req: ReportRequest):
    fmt = req.format.lower()
    
    # Audit log
    log_audit_event(
        action="COPILOT_REPORT_GEN",
        service_name="ai_service",
        username="Scientist",
        endpoint="/api/v1/copilot/report",
        details={"title": req.title, "format": req.format}
    )

    if fmt == "excel":
        content = report_generator.generate_excel_report(req.title, req.data or [])
        headers = {
            'Content-Disposition': f'attachment; filename="{req.title.replace(" ", "_")}.xlsx"',
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        return Response(content=content, headers=headers)
        
    elif fmt == "pdf":
        content = report_generator.generate_pdf_report(req.title, req.description, req.data or [])
        headers = {
            'Content-Disposition': f'attachment; filename="{req.title.replace(" ", "_")}.pdf"',
            'Content-Type': 'application/pdf'
        }
        return Response(content=content, headers=headers)
        
    elif fmt == "ppt":
        content = report_generator.generate_ppt_report(req.title, req.slides or [])
        headers = {
            'Content-Disposition': f'attachment; filename="{req.title.replace(" ", "_")}.json"',
            'Content-Type': 'application/json'
        }
        return Response(content=content, headers=headers)
        
    else:
        raise HTTPException(status_code=400, detail="Invalid report format. Choose excel, pdf, or ppt.")

@router.post("/dashboard")
def generate_dashboard_layout(req: DashboardRequest):
    layout = dashboard_generator.generate_dashboard(req.prompt)
    
    # Audit log
    log_audit_event(
        action="COPILOT_DASHBOARD_GEN",
        service_name="ai_service",
        username="Scientist",
        endpoint="/api/v1/copilot/dashboard",
        details={"prompt": req.prompt}
    )
    
    return layout

@router.post("/workflow")
def generate_workflow_graph(req: WorkflowRequest):
    graph = workflow_generator.generate_workflow(req.prompt)
    
    # Audit log
    log_audit_event(
        action="COPILOT_WORKFLOW_GEN",
        service_name="ai_service",
        username="Scientist",
        endpoint="/api/v1/copilot/workflow",
        details={"prompt": req.prompt}
    )
    
    return graph
