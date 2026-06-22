import uvicorn
import logging
import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
# Import models to ensure they are registered with SQLAlchemy Base
from app.models.workflow import WorkflowDefinition, WorkflowRun, WorkflowStep, WorkflowApproval, WorkflowEvent

# Initialize Database tables
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("workflow_service")

# Scheduler Setup
scheduler = BackgroundScheduler()

def run_scheduled_workflow(workflow_id: int):
    logger.info(f"Cron event fired: Triggering scheduled workflow ID {workflow_id}")
    db = SessionLocal()
    try:
        definition = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == workflow_id).first()
        if not definition or not definition.is_active:
            return

        run = WorkflowRun(
            workflow_id=workflow_id,
            status="PENDING",
            current_step_idx=0,
            logs=f"[{datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')}] Workflow triggered by cron schedule."
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        # Execute
        import asyncio
        from app.engine.executor import WorkflowExecutor
        exec_instance = WorkflowExecutor()
        
        # Run in separate thread event loop
        loop = asyncio.new_event_loop()
        loop.run_until_complete(exec_instance.execute_run(run.id))
        loop.close()

    except Exception as err:
        logger.error(f"Failed to execute cron-scheduled workflow {workflow_id}: {err}")
    finally:
        db.close()

def sync_scheduler_jobs():
    scheduler.remove_all_jobs()
    db = SessionLocal()
    try:
        definitions = db.query(WorkflowDefinition).filter(
            WorkflowDefinition.trigger_type == "SCHEDULED",
            WorkflowDefinition.is_active == True,
            WorkflowDefinition.cron_schedule != None
        ).all()

        for d in definitions:
            try:
                scheduler.add_job(
                    run_scheduled_workflow,
                    trigger=CronTrigger.from_crontab(d.cron_schedule),
                    args=[d.id],
                    id=f"workflow_{d.id}",
                    replace_existing=True
                )
                logger.info(f"Registered scheduled workflow: {d.name} (ID: {d.id}) on cron '{d.cron_schedule}'")
            except Exception as cron_err:
                logger.error(f"Error parsing cron schedule '{d.cron_schedule}' for workflow {d.id}: {cron_err}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    sync_scheduler_jobs()
    scheduler.start()
    logger.info("APScheduler background service initialized.")
    yield
    # Shutdown logic
    scheduler.shutdown()
    logger.info("APScheduler background service stopped.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.endpoints.workflows import router as workflows_router
app.include_router(workflows_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8009, reload=True)
