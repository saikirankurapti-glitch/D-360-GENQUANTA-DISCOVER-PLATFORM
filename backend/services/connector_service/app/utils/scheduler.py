import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.api.endpoints.connectors import sync_data_source_schema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MetadataScheduler")

class BackgroundSyncEngine:
    """
    A simple async loop scheduler that runs in the background of the microservice.
    Refreshes data source schemas automatically at scheduled intervals.
    """
    def __init__(self):
        self._running = False
        self._task = None

    def start(self) -> None:
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info("Background Metadata Sync Engine started.")

    def stop(self) -> None:
        if self._running:
            self._running = False
            if self._task:
                self._task.cancel()
            logger.info("Background Metadata Sync Engine stopped.")

    async def _run_loop(self) -> None:
        while self._running:
            try:
                # Sync metadata for all active data sources every 1 hour (3600 seconds)
                # In development, check every 300 seconds
                await asyncio.sleep(300)
                await self.sync_all_active_sources()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background sync loop: {str(e)}")

    async def sync_all_active_sources(self) -> None:
        db: Session = SessionLocal()
        try:
            from app.repositories.connector_repository import repo
            sources = repo.get_all_data_sources(db, active_only=True)
            for source in sources:
                logger.info(f"Automatically syncing schema for source: {source.name} (ID: {source.id})")
                try:
                    # Trigger the existing sync endpoint logic
                    await sync_data_source_schema(source.id, db)
                except Exception as sync_err:
                    logger.error(f"Failed to auto-sync source {source.id}: {str(sync_err)}")
        finally:
            db.close()

sync_engine = BackgroundSyncEngine()
