import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.connector import DataSource, ConnectionConfig, Entity, Field, Relationship, SyncHistory
from app.schemas.connector import DataSourceCreate, DataSourceUpdate, RelationshipCreate
from app.utils.security import encryptor

class ConnectorRepository:
    """
    Handles all CRUD operations for the Data Source metadata and schema catalog.
    """
    
    def get_data_source(self, db: Session, source_id: int) -> Optional[DataSource]:
        return db.query(DataSource).filter(DataSource.id == source_id).first()

    def get_all_data_sources(self, db: Session, active_only: bool = False) -> List[DataSource]:
        query = db.query(DataSource)
        if active_only:
            query = query.filter(DataSource.is_active == True)
        return query.all()

    def create_data_source(self, db: Session, obj_in: DataSourceCreate) -> DataSource:
        # Encrypt the credentials payload
        encrypted_creds = encryptor.encrypt(obj_in.credentials)
        additional_params_json = json.dumps(obj_in.additional_params or {})

        db_source = DataSource(
            name=obj_in.name,
            description=obj_in.description,
            connector_type=obj_in.connector_type,
            is_active=obj_in.is_active
        )
        db.add(db_source)
        db.flush()  # Populate id

        db_config = ConnectionConfig(
            data_source_id=db_source.id,
            encrypted_credentials=encrypted_creds,
            additional_params=additional_params_json
        )
        db.add(db_config)
        db.commit()
        db.refresh(db_source)
        return db_source

    def update_data_source(self, db: Session, source_id: int, obj_in: DataSourceUpdate) -> Optional[DataSource]:
        db_source = self.get_data_source(db, source_id)
        if not db_source:
            return None

        # Update core source attributes
        if obj_in.name is not None:
            db_source.name = obj_in.name
        if obj_in.description is not None:
            db_source.description = obj_in.description
        if obj_in.is_active is not None:
            db_source.is_active = obj_in.is_active

        # Update connection configs if provided
        if obj_in.credentials is not None or obj_in.additional_params is not None:
            db_config = db_source.config
            if not db_config:
                db_config = ConnectionConfig(data_source_id=db_source.id)
                db.add(db_config)
            
            if obj_in.credentials is not None:
                db_config.encrypted_credentials = encryptor.encrypt(obj_in.credentials)
            if obj_in.additional_params is not None:
                db_config.additional_params = json.dumps(obj_in.additional_params)

        db.commit()
        db.refresh(db_source)
        return db_source

    def delete_data_source(self, db: Session, source_id: int) -> bool:
        db_source = self.get_data_source(db, source_id)
        if not db_source:
            return False
        db.delete(db_source)
        db.commit()
        return True

    def log_sync_history(self, db: Session, source_id: int, status: str, 
                         records: int = 0, error: str = None, started_at: datetime = None) -> SyncHistory:
        """Logs a schema synchronization event."""
        started = started_at or datetime.utcnow()
        history = SyncHistory(
            data_source_id=source_id,
            sync_status=status,
            started_at=started,
            completed_at=datetime.utcnow(),
            records_synced=records,
            error_message=error
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        return history

    def get_sync_history(self, db: Session, source_id: int) -> List[SyncHistory]:
        return db.query(SyncHistory).filter(SyncHistory.data_source_id == source_id).order_by(SyncHistory.started_at.desc()).all()

    def get_decrypted_credentials(self, db: Session, source_id: int) -> Dict[str, Any]:
        """Utility to retrieve decrypted connection credentials safely."""
        db_source = self.get_data_source(db, source_id)
        if not db_source or not db_source.config:
            raise ValueError(f"No connection configuration found for data source {source_id}")
        raw_val = db_source.config.encrypted_credentials
        if raw_val.strip().startswith("{") and raw_val.strip().endswith("}"):
            try:
                return json.loads(raw_val)
            except Exception:
                pass
        try:
            return encryptor.decrypt(raw_val)
        except Exception:
            try:
                return json.loads(raw_val)
            except Exception:
                raise

    def refresh_entities_metadata(self, db: Session, source_id: int, schema_discovery: List[Dict[str, Any]]) -> int:
        """
        Synchronizes the database's metadata tables with the structures returned from schema discovery.
        Adds new tables/endpoints, updates datatypes/attributes, and prunes stale entities.
        """
        total_records = 0
        
        # 1. Fetch existing entities mapping
        existing_entities = db.query(Entity).filter(Entity.data_source_id == source_id).all()
        existing_entities_map = {ent.physical_name: ent for ent in existing_entities}
        
        discovered_physical_names = set()
        
        for entity_data in schema_discovery:
            phys_name = entity_data["physical_name"]
            discovered_physical_names.add(phys_name)
            
            # Find or create Entity
            if phys_name in existing_entities_map:
                db_entity = existing_entities_map[phys_name]
                db_entity.display_name = entity_data.get("display_name", db_entity.display_name)
                db_entity.description = entity_data.get("description", db_entity.description)
            else:
                db_entity = Entity(
                    data_source_id=source_id,
                    physical_name=phys_name,
                    display_name=entity_data.get("display_name", phys_name.replace("_", " ").title()),
                    description=entity_data.get("description"),
                    is_queryable=True
                )
                db.add(db_entity)
                db.flush()
                
            total_records += 1
            
            # 2. Sync columns/fields inside entity
            existing_fields = db.query(Field).filter(Field.entity_id == db_entity.id).all()
            existing_fields_map = {f.physical_name: f for f in existing_fields}
            
            discovered_field_names = set()
            
            for field_data in entity_data["fields"]:
                f_name = field_data["physical_name"]
                discovered_field_names.add(f_name)
                
                if f_name in existing_fields_map:
                    db_field = existing_fields_map[f_name]
                    db_field.display_name = field_data.get("display_name", db_field.display_name)
                    db_field.data_type = field_data.get("data_type", db_field.data_type)
                    db_field.is_nullable = field_data.get("is_nullable", db_field.is_nullable)
                    db_field.is_primary_key = field_data.get("is_primary_key", db_field.is_primary_key)
                    db_field.description = field_data.get("description", db_field.description)
                else:
                    db_field = Field(
                        entity_id=db_entity.id,
                        physical_name=f_name,
                        display_name=field_data.get("display_name", f_name.replace("_", " ").title()),
                        data_type=field_data.get("data_type", "string"),
                        is_nullable=field_data.get("is_nullable", True),
                        is_primary_key=field_data.get("is_primary_key", False),
                        description=field_data.get("description")
                    )
                    db.add(db_field)
                    
                total_records += 1
                
            # Delete fields that were not discovered in latest schema
            for f_name, db_field in existing_fields_map.items():
                if f_name not in discovered_field_names:
                    db.delete(db_field)
                    
        # Delete entities that were not discovered in latest schema
        for phys_name, db_entity in existing_entities_map.items():
            if phys_name not in discovered_physical_names:
                db.delete(db_entity)
                
        db.commit()
        return total_records

    # Logical relationship operations
    def create_relationship(self, db: Session, source_id: int, obj_in: RelationshipCreate) -> Relationship:
        db_rel = Relationship(
            data_source_id=source_id,
            source_entity_id=obj_in.source_entity_id,
            source_field_id=obj_in.source_field_id,
            target_entity_id=obj_in.target_entity_id,
            target_field_id=obj_in.target_field_id,
            cardinality=obj_in.cardinality
        )
        db.add(db_rel)
        db.commit()
        db.refresh(db_rel)
        return db_rel

    def get_relationships(self, db: Session, source_id: int) -> List[Relationship]:
        return db.query(Relationship).filter(Relationship.data_source_id == source_id).all()

    def delete_relationship(self, db: Session, rel_id: int) -> bool:
        db_rel = db.query(Relationship).filter(Relationship.id == rel_id).first()
        if not db_rel:
            return False
        db.delete(db_rel)
        db.commit()
        return True

    # Sync Checkpoints operations
    def get_sync_checkpoint(self, db: Session, source_id: int, entity_name: str):
        from app.models.connector import SyncCheckpoint
        return db.query(SyncCheckpoint).filter(
            SyncCheckpoint.data_source_id == source_id,
            SyncCheckpoint.entity_name == entity_name
        ).first()

    def save_sync_checkpoint(self, db: Session, source_id: int, entity_name: str, cursor_value: str, status: str):
        from app.models.connector import SyncCheckpoint
        db_chk = self.get_sync_checkpoint(db, source_id, entity_name)
        if not db_chk:
            db_chk = SyncCheckpoint(
                data_source_id=source_id,
                entity_name=entity_name
            )
            db.add(db_chk)
        db_chk.cursor_value = cursor_value
        db_chk.sync_status = status
        db_chk.last_sync_timestamp = datetime.utcnow()
        db.commit()
        db.refresh(db_chk)
        return db_chk

repo = ConnectorRepository()
