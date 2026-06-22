from typing import List
from sqlalchemy.orm import Session
from ..models.history import QueryHistory
from ..schemas.history import QueryHistoryCreate

class HistoryRepository:
    @staticmethod
    def get_history(db: Session, limit: int = 50) -> List[QueryHistory]:
        return db.query(QueryHistory).order_by(QueryHistory.created_at.desc()).limit(limit).all()

    @staticmethod
    def create_history_record(db: Session, obj_in: QueryHistoryCreate) -> QueryHistory:
        db_obj = QueryHistory(
            sql=obj_in.sql,
            status=obj_in.status,
            execution_time_ms=obj_in.execution_time_ms,
            row_count=obj_in.row_count,
            error_message=obj_in.error_message
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
