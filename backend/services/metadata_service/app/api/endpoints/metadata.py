from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
import json

from ...core.database import get_db
from ...repositories.metadata_repo import MetadataRepository
from ...schemas.metadata import MetadataFieldCreate, MetadataFieldResponse, MetadataEntityCreate, EntityDetailResponse, MetadataValueCreate
from ...models.metadata import MetadataField, MetadataEntity, MetadataValue

def get_user_from_request(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"id": "system", "email": "system-admin@analytix.com"}
    try:
        token = auth_header.split(" ")[1]
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_json = base64.b64decode(payload_b64).decode("utf-8")
        payload = json.loads(payload_json)
        return {
            "id": payload.get("sub", "system"),
            "email": payload.get("email") or payload.get("sub") or "system-admin@analytix.com"
        }
    except Exception:
        return {"id": "system", "email": "system-admin@analytix.com"}

router = APIRouter(prefix="/metadata", tags=["metadata"])

@router.get("/fields", response_model=List[MetadataFieldResponse])
def get_fields(db: Session = Depends(get_db)):
    return MetadataRepository.get_fields(db)

@router.post("/fields", response_model=MetadataFieldResponse, status_code=status.HTTP_201_CREATED)
def create_field(request: Request, obj_in: MetadataFieldCreate, db: Session = Depends(get_db)):
    field = MetadataRepository.get_field_by_name(db, name=obj_in.name)
    if field:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Metadata field with this name already exists."
        )
    db_field = MetadataRepository.create_field(db, obj_in=obj_in)
    
    user = get_user_from_request(request)
    from ...core.compliance_client import log_audit_event, log_entity_version
    audit_id = log_audit_event(
        action="CREATE_METADATA_FIELD",
        service_name="metadata_service",
        user_id=user["id"],
        username=user["email"],
        endpoint="/api/v1/metadata/fields",
        status="SUCCESS",
        details={"field_id": db_field.id, "field_name": db_field.name}
    )
    
    field_dict = {
        "id": db_field.id,
        "name": db_field.name,
        "display_name": db_field.display_name,
        "data_type": db_field.data_type,
        "description": db_field.description,
        "category": db_field.category
    }
    log_entity_version(
        entity_type="MetadataField",
        entity_id=str(db_field.id),
        data_json=json.dumps(field_dict),
        modified_by=user["email"],
        change_summary="Created metadata field definition",
        is_deleted=0,
        audit_log_id=audit_id
    )
    return db_field

@router.get("/entities", response_model=List[EntityDetailResponse])
def get_entities(entity_type: Optional[str] = None, db: Session = Depends(get_db)):
    entities = MetadataRepository.get_entities(db, entity_type=entity_type)
    return [MetadataRepository.consolidate_entity(e) for e in entities]

@router.post("/entities", response_model=EntityDetailResponse, status_code=status.HTTP_201_CREATED)
def create_entity(request: Request, obj_in: MetadataEntityCreate, db: Session = Depends(get_db)):
    entity = MetadataRepository.get_entity_by_key(db, entity_key=obj_in.entity_key)
    if entity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entity with this key already exists."
        )
    db_entity = MetadataRepository.create_entity(db, obj_in=obj_in)
    
    user = get_user_from_request(request)
    from ...core.compliance_client import log_audit_event, log_entity_version
    audit_id = log_audit_event(
        action="CREATE_METADATA_ENTITY",
        service_name="metadata_service",
        user_id=user["id"],
        username=user["email"],
        endpoint="/api/v1/metadata/entities",
        status="SUCCESS",
        details={"entity_key": db_entity.entity_key, "entity_type": db_entity.entity_type}
    )
    
    entity_dict = {
        "id": db_entity.id,
        "entity_key": db_entity.entity_key,
        "entity_type": db_entity.entity_type,
        "name": db_entity.name,
        "description": db_entity.description
    }
    log_entity_version(
        entity_type="MetadataEntity",
        entity_id=str(db_entity.id),
        data_json=json.dumps(entity_dict),
        modified_by=user["email"],
        change_summary="Created metadata entity record",
        is_deleted=0,
        audit_log_id=audit_id
    )
    return MetadataRepository.consolidate_entity(db_entity)

@router.get("/entities/{entity_key}", response_model=EntityDetailResponse)
def get_entity(entity_key: str, db: Session = Depends(get_db)):
    entity = MetadataRepository.get_entity_by_key(db, entity_key=entity_key)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found."
        )
    return MetadataRepository.consolidate_entity(entity)

@router.post("/bootstrap", status_code=status.HTTP_200_OK)
def bootstrap_mock_data(db: Session = Depends(get_db)):
    # 1. Define fields if not present
    fields_to_create = [
        MetadataFieldCreate(name="target_protein", display_name="Target Protein", data_type="string", description="Protein target of the assay", category="Assay"),
        MetadataFieldCreate(name="ic50_nm", display_name="IC50 (nM)", data_type="numeric", description="Half maximal inhibitory concentration", category="Assay"),
        MetadataFieldCreate(name="mw", display_name="Molecular Weight", data_type="numeric", description="Molecular weight of the compound", category="Chemistry"),
        MetadataFieldCreate(name="clogp", display_name="cLogP", data_type="numeric", description="Calculated octanol-water partition coefficient", category="Chemistry"),
        MetadataFieldCreate(name="hbd", display_name="H-Bond Donors", data_type="numeric", description="Hydrogen bond donors count", category="Chemistry"),
        MetadataFieldCreate(name="hba", display_name="H-Bond Acceptors", data_type="numeric", description="Hydrogen bond acceptors count", category="Chemistry"),
        MetadataFieldCreate(name="smiles", display_name="SMILES", data_type="string", description="SMILES string representation", category="Chemistry"),
        MetadataFieldCreate(name="study_phase", display_name="Study Phase", data_type="string", description="Clinical study phase", category="Clinical"),
        MetadataFieldCreate(name="principal_investigator", display_name="PI", data_type="string", description="Principal Investigator", category="Clinical"),
    ]

    field_map = {}
    for f in fields_to_create:
        existing = MetadataRepository.get_field_by_name(db, f.name)
        if not existing:
            existing = MetadataRepository.create_field(db, f)
        field_map[f.name] = existing.id

    # 2. Check if we already have entities, to avoid duplicates
    existing_entities = MetadataRepository.get_entities(db)
    if len(existing_entities) > 0:
        return {"message": "Database already contains seed data.", "fields": len(field_map), "entities": len(existing_entities)}

    # 3. Create Compound Entities
    compounds = [
        ("CMP-001", "Gefitinib Analog", "EGFR inhibitor study candidate", {
            "target_protein": "EGFR", "ic50_nm": "3.2", "mw": "446.9", "clogp": "3.8", "hbd": "1", "hba": "7",
            "smiles": "COCCOc1cc2c(Nc3ccc(F)c(Cl)c3)ncnc2cc1OC"
        }),
        ("CMP-002", "Imatinib Analog", "BCR-ABL inhibitor study candidate", {
            "target_protein": "BCR-ABL", "ic50_nm": "12.5", "mw": "493.6", "clogp": "4.2", "hbd": "2", "hba": "7",
            "smiles": "Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc4nccc(c5cccnc5)n4"
        }),
        ("CMP-003", "Vemurafenib Analog", "BRAF V600E mutant candidate", {
            "target_protein": "BRAF V600E", "ic50_nm": "0.8", "mw": "489.9", "clogp": "4.9", "hbd": "2", "hba": "5",
            "smiles": "CCCS(=O)(=O)Nc1ccc(F)c(C(=O)c2c[nH]c3ccc(Cl)cc23)c1F"
        }),
        ("CMP-004", "Lapatinib Analog", "HER2/EGFR dual inhibitor", {
            "target_protein": "HER2", "ic50_nm": "9.1", "mw": "581.1", "clogp": "5.1", "hbd": "1", "hba": "6",
            "smiles": "CS(=O)(=O)CCNc1ccc(c2ccc(OCc3cccc(F)c3)o2)cc1"
        }),
    ]

    entities_created = 0
    for key, name, desc, attrs in compounds:
        vals = []
        for attr_name, val_str in attrs.items():
            if attr_name in field_map:
                vals.append(MetadataValueCreate(field_id=field_map[attr_name], value=val_str))
        
        entity_in = MetadataEntityCreate(
            entity_key=key,
            entity_type="Compound",
            name=name,
            description=desc,
            values=vals
        )
        MetadataRepository.create_entity(db, entity_in)
        entities_created += 1

    # 4. Create Assay Entities
    assays = [
        ("ASSAY-101", "EGFR Kinase Assay", "In vitro kinase assay checking EGFR wildtype inhibition", {
            "target_protein": "EGFR", "ic50_nm": "4.5"
        }),
        ("ASSAY-102", "HER2 Cell Proliferation", "Cell-based assay evaluating BT474 breast cancer lines", {
            "target_protein": "HER2", "ic50_nm": "15.0"
        }),
    ]

    for key, name, desc, attrs in assays:
        vals = []
        for attr_name, val_str in attrs.items():
            if attr_name in field_map:
                vals.append(MetadataValueCreate(field_id=field_map[attr_name], value=val_str))
        
        entity_in = MetadataEntityCreate(
            entity_key=key,
            entity_type="Assay",
            name=name,
            description=desc,
            values=vals
        )
        MetadataRepository.create_entity(db, entity_in)
        entities_created += 1

    return {"message": "Bootstrap completed successfully.", "fields": len(field_map), "entities": entities_created}


# --- Metadata Federation Endpoints ---

from datetime import datetime
import json
from ...models.metadata import MetadataRelationship, MetadataVersion, MetadataSyncHistory
from ...schemas.metadata import (
    MetadataFederationSyncPayload, 
    MetadataRelationshipResponse, 
    MetadataVersionResponse, 
    MetadataSyncHistoryResponse
)

@router.post("/federation/sync", status_code=status.HTTP_200_OK)
def sync_federated_metadata(payload: MetadataFederationSyncPayload, db: Session = Depends(get_db)):
    start_time = datetime.utcnow()
    changes = []
    records_count = 0
    
    try:
        # 1. Compile new snapshot schema
        new_snapshot = {}
        for ent in payload.entities:
            new_snapshot[ent.entity_name] = {
                f.field_name: f.data_type
                for f in ent.fields
            }
            
        # 2. Get previous version to detect changes
        prev_version = db.query(MetadataVersion)\
            .filter(MetadataVersion.datasource_id == payload.datasource_id)\
            .order_by(MetadataVersion.version.desc())\
            .first()
            
        has_changes = False
        prev_snapshot = {}
        version_num = 1
        
        if prev_version:
            version_num = prev_version.version
            try:
                prev_snapshot = json.loads(prev_version.snapshot_data)
            except Exception:
                prev_snapshot = {}
                
            # Compare tables
            added_tables = set(new_snapshot.keys()) - set(prev_snapshot.keys())
            removed_tables = set(prev_snapshot.keys()) - set(new_snapshot.keys())
            
            if added_tables:
                has_changes = True
                changes.append(f"Added tables: {', '.join(added_tables)}")
            if removed_tables:
                has_changes = True
                changes.append(f"Removed tables: {', '.join(removed_tables)}")
                
            # Compare columns
            for tbl in set(new_snapshot.keys()) & set(prev_snapshot.keys()):
                new_cols = new_snapshot[tbl]
                prev_cols = prev_snapshot[tbl]
                
                added_cols = set(new_cols.keys()) - set(prev_cols.keys())
                removed_cols = set(prev_cols.keys()) - set(new_cols.keys())
                modified_cols = []
                
                for col in set(new_cols.keys()) & set(prev_cols.keys()):
                    if new_cols[col] != prev_cols[col]:
                        modified_cols.append(f"{col} ({prev_cols[col]} -> {new_cols[col]})")
                        
                if added_cols:
                    has_changes = True
                    changes.append(f"Table '{tbl}': added columns: {', '.join(added_cols)}")
                if removed_cols:
                    has_changes = True
                    changes.append(f"Table '{tbl}': removed columns: {', '.join(removed_cols)}")
                if modified_cols:
                    has_changes = True
                    changes.append(f"Table '{tbl}': altered columns: {', '.join(modified_cols)}")
        else:
            # First sync is always a change
            has_changes = True
            changes.append("Initial schema registration.")
            
        # 3. Synchronize metadata EAV catalogs
        # 3.1 Fetch current EAV entities for this source
        prefix = f"{payload.datasource_name}."
        existing_entities = db.query(MetadataEntity)\
            .filter(MetadataEntity.entity_type == "Table")\
            .filter(MetadataEntity.entity_key.like(f"{prefix}%"))\
            .all()
        existing_ent_map = {e.entity_key: e for e in existing_entities}
        
        synced_entity_keys = set()
        
        for ent in payload.entities:
            ent_key = f"{payload.datasource_name}.{ent.entity_name}"
            synced_entity_keys.add(ent_key)
            
            if ent_key in existing_ent_map:
                db_ent = existing_ent_map[ent_key]
                db_ent.description = ent.description or db_ent.description
            else:
                db_ent = MetadataEntity(
                    entity_key=ent_key,
                    entity_type="Table",
                    name=ent.entity_name,
                    description=ent.description or f"Federated table from {payload.datasource_name}"
                )
                db.add(db_ent)
                db.flush()
                
            records_count += 1
            
            # Fetch current attributes/values for this entity
            existing_values = db.query(MetadataValue)\
                .filter(MetadataValue.entity_id == db_ent.id)\
                .all()
            existing_val_map = {val.field.name: val for val in existing_values if val.field}
            
            synced_field_names = set()
            
            for fld in ent.fields:
                fld_name = f"{payload.datasource_name}.{ent.entity_name}.{fld.field_name}"
                synced_field_names.add(fld_name)
                
                # Retrieve or create MetadataField
                db_fld = db.query(MetadataField).filter(MetadataField.name == fld_name).first()
                if not db_fld:
                    db_fld = MetadataField(
                        name=fld_name,
                        display_name=fld.field_name,
                        data_type=fld.data_type,
                        description=fld.description or f"Column {fld.field_name}",
                        category=payload.datasource_name
                    )
                    db.add(db_fld)
                    db.flush()
                    
                # Retrieve or create MetadataValue mapping
                if fld_name in existing_val_map:
                    db_val = existing_val_map[fld_name]
                    db_val.value = fld.data_type
                else:
                    db_val = MetadataValue(
                        entity_id=db_ent.id,
                        field_id=db_fld.id,
                        value=fld.data_type
                    )
                    db.add(db_val)
                    
                records_count += 1
                
            # Prune removed fields
            for f_name, db_val in existing_val_map.items():
                if f_name not in synced_field_names:
                    db.delete(db_val)
                    
        # Prune removed entities
        for e_key, db_ent in existing_ent_map.items():
            if e_key not in synced_entity_keys:
                db.delete(db_ent)
                
        # 4. Synchronize Relationships
        # Clear out previous relationships for this source
        db.query(MetadataRelationship).filter(MetadataRelationship.datasource_id == payload.datasource_id).delete()
        
        for rel in payload.relationships:
            db_rel = MetadataRelationship(
                datasource_id=payload.datasource_id,
                source_entity_key=f"{payload.datasource_name}.{rel.source_entity_name}",
                source_field_name=rel.source_field_name,
                target_entity_key=f"{payload.datasource_name}.{rel.target_entity_name}",
                target_field_name=rel.target_field_name,
                cardinality=rel.cardinality
            )
            db.add(db_rel)
            records_count += 1
            
        # 5. Save Schema Snapshot versioning
        changes_desc = "; ".join(changes) if changes else "No schema changes detected."
        if has_changes:
            if prev_version:
                version_num += 1
            db_ver = MetadataVersion(
                datasource_id=payload.datasource_id,
                version=version_num,
                snapshot_data=json.dumps(new_snapshot),
                changes_detected=changes_desc
            )
            db.add(db_ver)
            
        # 6. Log Sync History
        db_hist = MetadataSyncHistory(
            datasource_id=payload.datasource_id,
            datasource_name=payload.datasource_name,
            status="SUCCESS",
            started_at=start_time,
            completed_at=datetime.utcnow(),
            records_synced=records_count,
            changes_detected=changes_desc
        )
        db.add(db_hist)
        
        db.commit()
        return {
            "status": "SUCCESS",
            "version": version_num,
            "changes_detected": changes_desc,
            "records_synced": records_count
        }
        
    except Exception as e:
        db.rollback()
        # Log failure
        db_hist = MetadataSyncHistory(
            datasource_id=payload.datasource_id,
            datasource_name=payload.datasource_name,
            status="FAILED",
            started_at=start_time,
            completed_at=datetime.utcnow(),
            records_synced=0,
            error_message=str(e)
        )
        db.add(db_hist)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Federated sync failed: {str(e)}"
        )


@router.get("/federation/relationships", response_model=List[MetadataRelationshipResponse])
def get_federated_relationships(db: Session = Depends(get_db)):
    return db.query(MetadataRelationship).all()


@router.get("/federation/versions/{datasource_id}", response_model=List[MetadataVersionResponse])
def get_federated_versions(datasource_id: int, db: Session = Depends(get_db)):
    return db.query(MetadataVersion)\
        .filter(MetadataVersion.datasource_id == datasource_id)\
        .order_by(MetadataVersion.version.desc())\
        .all()


@router.get("/federation/history", response_model=List[MetadataSyncHistoryResponse])
def get_federated_history(db: Session = Depends(get_db)):
    return db.query(MetadataSyncHistory)\
        .order_by(MetadataSyncHistory.completed_at.desc())\
        .all()

