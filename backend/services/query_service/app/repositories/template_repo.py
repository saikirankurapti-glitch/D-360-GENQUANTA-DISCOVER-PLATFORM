from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.template import QueryTemplate
from ..schemas.template import QueryTemplateCreate

class TemplateRepository:
    
    @staticmethod
    def get_templates(db: Session) -> List[QueryTemplate]:
        return db.query(QueryTemplate).all()

    @staticmethod
    def get_template_by_id(db: Session, template_id: int) -> Optional[QueryTemplate]:
        return db.query(QueryTemplate).filter(QueryTemplate.id == template_id).first()

    @staticmethod
    def create_template(db: Session, obj_in: QueryTemplateCreate) -> QueryTemplate:
        db_obj = QueryTemplate(
            name=obj_in.name,
            description=obj_in.description,
            layout_json=obj_in.layout_json,
            sql_preview=obj_in.sql_preview,
            created_by=obj_in.created_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete_template(db: Session, template_id: int) -> bool:
        db_obj = db.query(QueryTemplate).filter(QueryTemplate.id == template_id).first()
        if not db_obj:
            return False
        db.delete(db_obj)
        db.commit()
        return True

    @staticmethod
    def duplicate_template(db: Session, template_id: int) -> Optional[QueryTemplate]:
        source = db.query(QueryTemplate).filter(QueryTemplate.id == template_id).first()
        if not source:
            return None
            
        duplicated = QueryTemplate(
            name=f"Copy of {source.name}",
            description=source.description,
            layout_json=source.layout_json,
            sql_preview=source.sql_preview,
            created_by=source.created_by
        )
        db.add(duplicated)
        db.commit()
        db.refresh(duplicated)
        return duplicated
