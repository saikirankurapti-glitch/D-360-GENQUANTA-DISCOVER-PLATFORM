from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from ..models.metadata import MetadataField, MetadataEntity, MetadataValue
from ..schemas.metadata import MetadataFieldCreate, MetadataEntityCreate, MetadataValueCreate, EntityDetailResponse, FieldValueDetail

class MetadataRepository:
    
    # --- Field Operations ---
    @staticmethod
    def get_field_by_name(db: Session, name: str) -> Optional[MetadataField]:
        return db.query(MetadataField).filter(MetadataField.name == name).first()

    @staticmethod
    def get_fields(db: Session) -> List[MetadataField]:
        return db.query(MetadataField).all()

    @staticmethod
    def create_field(db: Session, obj_in: MetadataFieldCreate) -> MetadataField:
        db_obj = MetadataField(
            name=obj_in.name,
            display_name=obj_in.display_name,
            data_type=obj_in.data_type,
            description=obj_in.description,
            category=obj_in.category or "General",
            is_required=obj_in.is_required or False
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # --- Entity Operations ---
    @staticmethod
    def get_entity_by_key(db: Session, entity_key: str) -> Optional[MetadataEntity]:
        return db.query(MetadataEntity).filter(MetadataEntity.entity_key == entity_key).first()

    @staticmethod
    def get_entities(db: Session, entity_type: Optional[str] = None) -> List[MetadataEntity]:
        query = db.query(MetadataEntity).options(
            joinedload(MetadataEntity.values).joinedload(MetadataValue.field)
        )
        if entity_type:
            query = query.filter(MetadataEntity.entity_type == entity_type)
        return query.all()

    @staticmethod
    def create_entity(db: Session, obj_in: MetadataEntityCreate) -> MetadataEntity:
        db_entity = MetadataEntity(
            entity_key=obj_in.entity_key,
            entity_type=obj_in.entity_type,
            name=obj_in.name,
            description=obj_in.description
        )
        db.add(db_entity)
        db.commit()
        db.refresh(db_entity)

        # Add values if provided
        for val_in in obj_in.values:
            db_val = MetadataValue(
                entity_id=db_entity.id,
                field_id=val_in.field_id,
                value=val_in.value
            )
            db.add(db_val)
        
        if obj_in.values:
            db.commit()
            db.refresh(db_entity)
            
        return db_entity

    @staticmethod
    def consolidate_entity(entity: MetadataEntity) -> EntityDetailResponse:
        attributes = {}
        details = []
        
        for val in entity.values:
            field = val.field
            if field:
                attributes[field.name] = val.value
                details.append(FieldValueDetail(
                    field_name=field.name,
                    display_name=field.display_name,
                    category=field.category,
                    data_type=field.data_type,
                    value=val.value
                ))
                
        return EntityDetailResponse(
            id=entity.id,
            entity_key=entity.entity_key,
            entity_type=entity.entity_type,
            name=entity.name,
            description=entity.description,
            attributes=attributes,
            details=details
        )
