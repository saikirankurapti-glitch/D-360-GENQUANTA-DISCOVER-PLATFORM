import json
import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler

from ...core.database import get_db
from ...models.analysis import AnalysisWorkspace
from ...schemas.analysis_schema import AnalysisWorkspaceCreate, AnalysisWorkspaceResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Helper function for 4PL dose-response fit
def logistic_4pl(x, hill_slope, ec50, min_resp, max_resp):
    """
    4-Parameter Logistic Model:
    y = min_resp + (max_resp - min_resp) / (1 + 10**(hill_slope * (log10(ec50) - x)))
    Where:
    x = log10(concentration)
    """
    return min_resp + (max_resp - min_resp) / (1.0 + 10.0 ** (hill_slope * (np.log10(ec50) - x)))

@router.post("/dose-response")
def fit_dose_response(payload: Dict[str, Any]):
    """
    Fits a 4-Parameter Logistic (4PL) regression to concentration-response data.
    """
    concentrations = payload.get("concentrations", [])
    responses = payload.get("responses", [])

    if len(concentrations) < 4 or len(responses) < 4:
        raise HTTPException(
            status_code=400,
            detail="At least 4 data points are required to fit a 4-parameter logistic curve."
        )

    try:
        x_data = np.array(concentrations, dtype=float)
        y_data = np.array(responses, dtype=float)

        # Drop NaNs or infinite values
        valid_idx = np.isfinite(x_data) & np.isfinite(y_data)
        x_data = x_data[valid_idx]
        y_data = y_data[valid_idx]

        if len(x_data) < 4:
            raise ValueError("Insufficient valid numeric data points.")

        # x_log represents log10(concentration). If concentration <= 0, filter it out.
        pos_idx = x_data > 0
        x_data = x_data[pos_idx]
        y_data = y_data[pos_idx]
        x_log = np.log10(x_data)

        # Parameter initial estimates
        min_y = np.min(y_data)
        max_y = np.max(y_data)
        
        # Estimate EC50 as the median concentration
        ec50_est = np.median(x_data)
        hill_est = 1.0 if y_data[0] < y_data[-1] else -1.0

        p0 = [hill_est, ec50_est, min_y, max_y]
        
        # Boundaries to avoid overflows
        # [hill_slope, ec50, min_resp, max_resp]
        lower_bounds = [-10.0, np.min(x_data) * 0.01, min_y - abs(min_y)*0.5 - 1.0, min_y]
        upper_bounds = [10.0, np.max(x_data) * 100.0, max_y, max_y + abs(max_y)*0.5 + 1.0]

        popt, pcov = curve_fit(
            logistic_4pl, 
            x_log, 
            y_data, 
            p0=p0, 
            bounds=(lower_bounds, upper_bounds),
            maxfev=5000
        )

        hill_slope, ec50, min_resp, max_resp = popt

        # R-squared calculation
        residuals = y_data - logistic_4pl(x_log, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y_data - np.mean(y_data))**2)
        r_squared = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

        # Generate fitted points for plotting
        x_fit_log = np.linspace(np.min(x_log) - 0.5, np.max(x_log) + 0.5, 100)
        x_fit = 10.0 ** x_fit_log
        y_fit = logistic_4pl(x_fit_log, *popt)

        return {
            "success": True,
            "ec50": float(ec50),
            "hill_slope": float(hill_slope),
            "min_response": float(min_resp),
            "max_response": float(max_resp),
            "r_squared": float(r_squared),
            "curve_points": {
                "concentrations": x_fit.tolist(),
                "responses": y_fit.tolist()
            }
        }
    except Exception as e:
        # Fallback parameters or error return
        return {
            "success": False,
            "error": f"Fit failed: {str(e)}",
            "ec50": 0.0,
            "hill_slope": 0.0,
            "min_response": 0.0,
            "max_response": 0.0,
            "r_squared": 0.0,
            "curve_points": {
                "concentrations": [],
                "responses": []
            }
        }


@router.post("/pca")
def run_pca(payload: Dict[str, Any]):
    """
    Performs Principal Component Analysis on the provided dataset.
    """
    rows = payload.get("rows", [])
    columns = payload.get("columns", [])
    features = payload.get("features", [])

    if not rows or not features:
        raise HTTPException(status_code=400, detail="Missing dataset rows or features selection")

    try:
        df = pd.DataFrame(rows, columns=columns)
        df_num = df[features].apply(pd.to_numeric, errors='coerce').fillna(0.0)

        # Standardize features
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df_num)

        pca = PCA(n_components=min(len(features), 2))
        pca_coords = pca.fit_transform(scaled_data)

        # Formulate loading vectors
        loadings = pca.components_
        loading_list = []
        for i, feat in enumerate(features):
            loading_list.append({
                "feature": feat,
                "pc1": float(loadings[0, i]) if loadings.shape[0] > 0 else 0.0,
                "pc2": float(loadings[1, i]) if loadings.shape[0] > 1 else 0.0
            })

        pc1_coords = pca_coords[:, 0].tolist() if pca_coords.shape[1] > 0 else [0.0] * len(rows)
        pc2_coords = pca_coords[:, 1].tolist() if pca_coords.shape[1] > 1 else [0.0] * len(rows)

        return {
            "coords": [{"pc1": x, "pc2": y} for x, y in zip(pc1_coords, pc2_coords)],
            "explained_variance": [float(v) for v in pca.explained_variance_ratio_],
            "loadings": loading_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PCA failed: {str(e)}")


@router.post("/tsne")
def run_tsne(payload: Dict[str, Any]):
    """
    Performs t-SNE dimensionality reduction.
    """
    rows = payload.get("rows", [])
    columns = payload.get("columns", [])
    features = payload.get("features", [])
    perplexity = float(payload.get("perplexity", 30))
    
    if len(rows) < 5:
        raise HTTPException(status_code=400, detail="At least 5 rows are required for t-SNE")

    try:
        df = pd.DataFrame(rows, columns=columns)
        df_num = df[features].apply(pd.to_numeric, errors='coerce').fillna(0.0)

        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df_num)

        # adjust perplexity if it exceeds sample size
        actual_perplexity = min(perplexity, len(rows) - 1)
        tsne = TSNE(n_components=2, perplexity=actual_perplexity, random_state=42, max_iter=1000)
        coords = tsne.fit_transform(scaled_data)

        return {
            "coords": [{"x": float(c[0]), "y": float(c[1])} for c in coords]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"t-SNE failed: {str(e)}")


@router.post("/clustering")
def run_clustering(payload: Dict[str, Any]):
    """
    Performs K-Means or DBSCAN clustering.
    """
    rows = payload.get("rows", [])
    columns = payload.get("columns", [])
    features = payload.get("features", [])
    algorithm = payload.get("algorithm", "kmeans").lower()
    
    if not rows or not features:
        raise HTTPException(status_code=400, detail="Missing dataset rows or features selection")

    try:
        df = pd.DataFrame(rows, columns=columns)
        df_num = df[features].apply(pd.to_numeric, errors='coerce').fillna(0.0)

        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df_num)

        if algorithm == "dbscan":
            eps = float(payload.get("eps", 0.5))
            min_samples = int(payload.get("min_samples", 5))
            db = DBSCAN(eps=eps, min_samples=min_samples)
            labels = db.fit_predict(scaled_data)
        else:
            n_clusters = int(payload.get("n_clusters", 3))
            n_clusters = min(n_clusters, len(rows))
            km = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
            labels = km.fit_predict(scaled_data)

        return {
            "labels": [int(l) for l in labels]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering failed: {str(e)}")


@router.post("/correlation")
def run_correlation(payload: Dict[str, Any]):
    """
    Computes Pearson correlation matrix.
    """
    rows = payload.get("rows", [])
    columns = payload.get("columns", [])
    features = payload.get("features", [])

    if not rows or not features:
        raise HTTPException(status_code=400, detail="Missing dataset rows or features selection")

    try:
        df = pd.DataFrame(rows, columns=columns)
        df_num = df[features].apply(pd.to_numeric, errors='coerce')
        
        corr = df_num.corr(method='pearson').fillna(0.0)
        
        return {
            "matrix": corr.values.tolist(),
            "columns": corr.columns.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Correlation computation failed: {str(e)}")


# CRUD endpoints for saved workspaces
@router.post("/workspaces", response_model=AnalysisWorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(obj_in: AnalysisWorkspaceCreate, db: Session = Depends(get_db)):
    db_obj = AnalysisWorkspace(
        name=obj_in.name,
        description=obj_in.description,
        query_history_id=obj_in.query_history_id,
        dataset_json=obj_in.dataset_json,
        configs_json=obj_in.configs_json,
        created_at=datetime.utcnow().isoformat()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.get("/workspaces", response_model=List[AnalysisWorkspaceResponse])
def list_workspaces(db: Session = Depends(get_db)):
    return db.query(AnalysisWorkspace).all()


@router.get("/workspaces/{id}", response_model=AnalysisWorkspaceResponse)
def get_workspace(id: int, db: Session = Depends(get_db)):
    workspace = db.query(AnalysisWorkspace).filter(AnalysisWorkspace.id == id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Analysis workspace not found")
    return workspace


@router.delete("/workspaces/{id}")
def delete_workspace(id: int, db: Session = Depends(get_db)):
    workspace = db.query(AnalysisWorkspace).filter(AnalysisWorkspace.id == id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Analysis workspace not found")
    db.delete(workspace)
    db.commit()
    return {"message": "Workspace deleted successfully"}


@router.get("/dashboard-analytics")
def get_dashboard_analytics():
    import psycopg2
    import hashlib
    from datetime import datetime
    
    # Helper connection logic
    def get_db_conn(db_name: str):
        for pwd in ["postgres", "Saikiran@123"]:
            try:
                return psycopg2.connect(
                    host="localhost",
                    port=5432,
                    user="postgres",
                    password=pwd,
                    database=db_name
                )
            except Exception:
                continue
        return None

    # Retrieve Metadata Catalog data
    metadata_data = {"fields": [], "entities": [], "values": [], "relationships_count": 0}
    conn_meta = get_db_conn("genquantaa_metadata")
    if conn_meta:
        try:
            cur = conn_meta.cursor()
            # Fields
            cur.execute("SELECT id, name, display_name, category, data_type FROM metadata.metadata_fields;")
            metadata_data["fields"] = [
                {"id": r[0], "name": r[1], "display_name": r[2], "category": r[3], "data_type": r[4]}
                for r in cur.fetchall()
            ]
            # Entities
            cur.execute("SELECT id, entity_key, entity_type, name, description FROM metadata.metadata_entities;")
            metadata_data["entities"] = [
                {"id": r[0], "entity_key": r[1], "entity_type": r[2], "name": r[3], "description": r[4]}
                for r in cur.fetchall()
            ]
            # Values
            cur.execute("SELECT entity_id, field_id, value FROM metadata.metadata_values;")
            metadata_data["values"] = [
                {"entity_id": r[0], "field_id": r[1], "value": r[2]}
                for r in cur.fetchall()
            ]
            # Relationships count
            cur.execute("SELECT COUNT(*) FROM metadata.metadata_relationships;")
            metadata_data["relationships_count"] = cur.fetchone()[0]
        except Exception as e:
            print(f"Metadata fetch error: {e}")
        finally:
            conn_meta.close()

    # Retrieve Bioinformatics data
    bioinfo_data = {"sequences": [], "annotations": [], "alignments": [], "clusters": []}
    conn_bio = get_db_conn("genquantaa_bioinfo")
    if conn_bio:
        try:
            cur = conn_bio.cursor()
            # Sequences
            cur.execute("SELECT id, sequence_id, name, sequence_type, description, created_at FROM bio.sequences;")
            bioinfo_data["sequences"] = [
                {"id": r[0], "sequence_id": r[1], "name": r[2], "sequence_type": r[3], "description": r[4], "created_at": r[5].isoformat() if r[5] else None}
                for r in cur.fetchall()
            ]
            # Annotations
            cur.execute("SELECT sequence_id, feature_type, name, start, \"end\" FROM bio.sequence_annotations;")
            bioinfo_data["annotations"] = [
                {"sequence_id": r[0], "feature_type": r[1], "name": r[2], "start": r[3], "end": r[4]}
                for r in cur.fetchall()
            ]
            # Alignments
            cur.execute("SELECT id, name, score FROM bio.alignments;")
            bioinfo_data["alignments"] = [
                {"id": r[0], "name": r[1], "score": r[2]}
                for r in cur.fetchall()
            ]
            # Clusters
            cur.execute("SELECT id, name, matrix_json, linkage_json FROM bio.sequence_clusters;")
            bioinfo_data["clusters"] = [
                {"id": r[0], "name": r[1], "matrix": json.loads(r[2]) if r[2] else {}, "linkage": json.loads(r[3]) if r[3] else []}
                for r in cur.fetchall()
            ]
        except Exception as e:
            print(f"Bioinformatics fetch error: {e}")
        finally:
            conn_bio.close()

    # Retrieve Workflow data
    workflow_data = {"definitions": [], "runs": [], "steps": [], "approvals": []}
    conn_wf = get_db_conn("genquantaa_workflow")
    if conn_wf:
        try:
            cur = conn_wf.cursor()
            # Definitions
            cur.execute("SELECT id, name, description FROM workflow.workflow_definitions;")
            workflow_data["definitions"] = [
                {"id": r[0], "name": r[1], "description": r[2]}
                for r in cur.fetchall()
            ]
            # Runs
            cur.execute("SELECT id, workflow_id, status, started_at, finished_at FROM workflow.workflow_runs;")
            workflow_data["runs"] = [
                {
                    "id": r[0],
                    "workflow_id": r[1],
                    "status": r[2],
                    "started_at": r[3].isoformat() if r[3] else None,
                    "finished_at": r[4].isoformat() if r[4] else None
                }
                for r in cur.fetchall()
            ]
            # Steps
            cur.execute("SELECT id, run_id, step_name, node_type, status, execution_time_ms FROM workflow.workflow_steps;")
            workflow_data["steps"] = [
                {"id": r[0], "run_id": r[1], "step_name": r[2], "node_type": r[3], "status": r[4], "execution_time_ms": r[5]}
                for r in cur.fetchall()
            ]
            # Approvals
            cur.execute("SELECT id, run_id, status, requested_at, completed_at, approved_by FROM workflow.workflow_approvals;")
            workflow_data["approvals"] = [
                {
                    "id": r[0], 
                    "run_id": r[1], 
                    "status": r[2], 
                    "requested_at": r[3].isoformat() if r[3] else None, 
                    "completed_at": r[4].isoformat() if r[4] else None,
                    "approved_by": r[5]
                }
                for r in cur.fetchall()
            ]
        except Exception as e:
            print(f"Workflow fetch error: {e}")
        finally:
            conn_wf.close()

    # Retrieve Compliance & Audit data
    audit_data = {"signatures": [], "signature_events": [], "entity_versions": [], "logs": []}
    conn_audit = get_db_conn("genquantaa_audit")
    if conn_audit:
        try:
            cur = conn_audit.cursor()
            # Signatures
            cur.execute("SELECT id, username, created_at FROM audit.electronic_signatures;")
            audit_data["signatures"] = [
                {"id": r[0], "username": r[1], "created_at": r[2].isoformat() if r[2] else None}
                for r in cur.fetchall()
            ]
            # Events
            cur.execute("SELECT id, action_type, timestamp FROM audit.signature_events;")
            audit_data["signature_events"] = [
                {"id": r[0], "action_type": r[1], "timestamp": r[2].isoformat() if r[2] else None}
                for r in cur.fetchall()
            ]
            # Versions
            cur.execute("SELECT id, entity_type, entity_id, version FROM audit.entity_versions;")
            audit_data["entity_versions"] = [
                {"id": r[0], "entity_type": r[1], "entity_id": r[2], "version": r[3]}
                for r in cur.fetchall()
            ]
            # Logs
            cur.execute("SELECT id, timestamp, username, action, service_name, status, previous_hash, hash, user_id FROM audit.audit_logs ORDER BY timestamp ASC;")
            audit_data["logs"] = [
                {
                    "id": r[0], 
                    "timestamp": r[1].isoformat() if r[1] else None, 
                    "username": r[2], 
                    "action": r[3], 
                    "service_name": r[4], 
                    "status": r[5], 
                    "previous_hash": r[6], 
                    "hash": r[7],
                    "user_id": r[8]
                }
                for r in cur.fetchall()
            ]
        except Exception as e:
            print(f"Audit fetch error: {e}")
        finally:
            conn_audit.close()

    # Retrieve AI Copilot data
    ai_data = {"sessions": [], "messages": []}
    conn_ai = get_db_conn("genquantaa_ai")
    if conn_ai:
        try:
            cur = conn_ai.cursor()
            # Sessions
            cur.execute("SELECT id, title, created_at FROM ai.chat_sessions;")
            ai_data["sessions"] = [
                {"id": r[0], "title": r[1], "created_at": r[2].isoformat() if r[2] else None}
                for r in cur.fetchall()
            ]
            # Messages
            cur.execute("SELECT id, session_id, role, content, created_at FROM ai.chat_messages;")
            ai_data["messages"] = [
                {"id": r[0], "session_id": r[1], "role": r[2], "content": r[3], "created_at": r[4].isoformat() if r[4] else None}
                for r in cur.fetchall()
            ]
        except Exception as e:
            print(f"AI Copilot fetch error: {e}")
        finally:
            conn_ai.close()

    # Retrieve Connectors details
    connector_sources = []
    conn_conn = get_db_conn("genquantaa_connector")
    if conn_conn:
        try:
            cur = conn_conn.cursor()
            cur.execute("SELECT id, name, connector_type, is_active FROM connector.data_sources;")
            connector_sources = [
                {"id": r[0], "name": r[1], "connector_type": r[2], "is_active": r[3]}
                for r in cur.fetchall()
            ]
        except Exception as e:
            print(f"Connector fetch error: {e}")
        finally:
            conn_conn.close()

    # Processing details into structured dictionaries
    fields_map = {f["id"]: f["name"] for f in metadata_data["fields"]}
    
    # Organize EAV values by entity ID
    entity_attrs = {}
    for val in metadata_data["values"]:
        e_id = val["entity_id"]
        f_name = fields_map.get(val["field_id"])
        if f_name:
            if e_id not in entity_attrs:
                entity_attrs[e_id] = {}
            entity_attrs[e_id][f_name] = val["value"]

    # Filter entities
    compounds = []
    assays = []
    for ent in metadata_data["entities"]:
        ent_id = ent["id"]
        attrs = entity_attrs.get(ent_id, {})
        ent_with_attrs = {**ent, "attributes": attrs}
        if ent["entity_type"] == "Compound":
            compounds.append(ent_with_attrs)
        elif ent["entity_type"] == "Assay":
            assays.append(ent_with_attrs)

    # 1. Compound Analytics Calculations
    total_compounds = len(compounds)
    compounds_by_target = {}
    compounds_by_project = {}
    mw_values = []
    clogp_values = []
    hbd_values = []
    hba_values = []
    tpsa_values = []
    lipinski_compliance = {"compliant": 0, "non_compliant": 0}
    
    for c in compounds:
        attrs = c["attributes"]
        target = attrs.get("target_protein", "Unknown")
        compounds_by_target[target] = compounds_by_target.get(target, 0) + 1
        
        project = attrs.get("project", "Unknown")
        compounds_by_project[project] = compounds_by_project.get(project, 0) + 1
        
        try:
            mw = float(attrs.get("mw", 0))
            if mw > 0: mw_values.append(mw)
        except ValueError: mw = 0
        
        try:
            clogp = float(attrs.get("clogp", 0))
            clogp_values.append(clogp)
        except ValueError: clogp = 0
        
        try:
            hbd = int(attrs.get("hbd", 0))
            hbd_values.append(hbd)
        except ValueError: hbd = 0
            
        try:
            hba = int(attrs.get("hba", 0))
            hba_values.append(hba)
        except ValueError: hba = 0
            
        # Lipinski compliance check
        violations = 0
        if mw > 500: violations += 1
        if clogp > 5: violations += 1
        if hbd > 5: violations += 1
        if hba > 10: violations += 1
        
        if violations <= 1:
            lipinski_compliance["compliant"] += 1
        else:
            lipinski_compliance["non_compliant"] += 1

    # 2. Assay Analytics Calculations
    total_assays = len(assays)
    assays_by_target = {}
    ic50_values = []
    ec50_values = []
    active_assays_count = 0
    top_performing_compounds = []
    
    for a in assays:
        attrs = a["attributes"]
        target = attrs.get("target_protein", "Unknown")
        assays_by_target[target] = assays_by_target.get(target, 0) + 1
        
        try:
            ic50 = float(attrs.get("ic50_nm", 0))
            if ic50 > 0:
                ic50_values.append(ic50)
                if ic50 < 100.0:
                    active_assays_count += 1
                    top_performing_compounds.append({
                        "compound_id": attrs.get("compound_id", "Unknown"),
                        "target": target,
                        "ic50": ic50,
                        "name": a["name"]
                    })
        except ValueError: pass
        
        try:
            ec50 = float(attrs.get("ec50_nm", 0))
            if ec50 > 0: ec50_values.append(ec50)
        except ValueError: pass

    top_performing_compounds = sorted(top_performing_compounds, key=lambda x: x["ic50"])[:10]
    assay_success_rate = round((active_assays_count / total_assays) * 100, 2) if total_assays > 0 else 0

    # 3. Bioinformatics Calculations
    total_sequences = len(bioinfo_data["sequences"])
    seq_type_dist = {}
    organism_dist = {"Homo sapiens": 0, "Other": 0}
    mutation_count = 0
    
    for s in bioinfo_data["sequences"]:
        seq_type_dist[s["sequence_type"]] = seq_type_dist.get(s["sequence_type"], 0) + 1
        desc = s["description"] or ""
        if "Homo sapiens" in desc or "human" in desc.lower():
            organism_dist["Homo sapiens"] += 1
        else:
            organism_dist["Other"] += 1
            
        if "mutation" in desc.lower() or "variant" in desc.lower() or "mutant" in desc.lower():
            mutation_count += 1

    # 4. Workflow Calculations
    total_workflows = len(workflow_data["runs"])
    workflow_success_count = 0
    workflow_failure_count = 0
    workflow_running_count = 0
    workflow_durations = []
    workflow_utilization = {}
    workflow_sla_compliant = 0
    
    for r in workflow_data["runs"]:
        if r["status"] == "COMPLETED":
            workflow_success_count += 1
        elif r["status"] == "FAILED":
            workflow_failure_count += 1
        else:
            workflow_running_count += 1
            
        workflow_utilization[r["workflow_id"]] = workflow_utilization.get(r["workflow_id"], 0) + 1
        
        if r["started_at"] and r["finished_at"]:
            start = datetime.fromisoformat(r["started_at"])
            end = datetime.fromisoformat(r["finished_at"])
            duration_sec = (end - start).total_seconds()
            workflow_durations.append(duration_sec)
            
            if duration_sec < 60.0:
                workflow_sla_compliant += 1

    workflow_success_rate = round((workflow_success_count / total_workflows) * 100, 2) if total_workflows > 0 else 0
    workflow_failure_rate = round((workflow_failure_count / total_workflows) * 100, 2) if total_workflows > 0 else 0
    avg_workflow_duration = round(sum(workflow_durations) / len(workflow_durations), 2) if workflow_durations else 0
    workflow_sla_compliance_rate = round((workflow_sla_compliant / total_workflows) * 100, 2) if total_workflows > 0 else 0

    # 5. Compliance Calculations
    total_compliance_events = len(audit_data["logs"])
    audit_events_by_type = {}
    audit_events_by_user = {}
    signature_trends = {}
    compliance_violations = 0
    
    def get_audit_trail_hash(timestamp_str, action, service_name, user_id, prev_hash):
        payload = f"{timestamp_str}|{action}|{service_name}|{user_id or ''}|{prev_hash or ''}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    for idx, log in enumerate(audit_data["logs"]):
        action = log["action"]
        audit_events_by_type[action] = audit_events_by_type.get(action, 0) + 1
        
        user = log["username"] or "unknown"
        audit_events_by_user[user] = audit_events_by_user.get(user, 0) + 1
        
        expected_hash = get_audit_trail_hash(
            timestamp_str=log["timestamp"],
            action=log["action"],
            service_name=log["service_name"],
            user_id=log["user_id"],
            prev_hash=log["previous_hash"]
        )
        if log["hash"] != expected_hash:
            compliance_violations += 1

    for sig in audit_data["signatures"]:
        date_str = sig["created_at"][:10] if sig["created_at"] else "Unknown"
        signature_trends[date_str] = signature_trends.get(date_str, 0) + 1

    compliance_health_score = round(100 - (compliance_violations / total_compliance_events * 100), 2) if total_compliance_events > 0 else 100.0

    # 6. AI Scientist Copilot Calculations
    total_chat_sessions = len(ai_data["sessions"])
    total_chat_messages = len(ai_data["messages"])
    total_ai_queries = len([m for m in ai_data["messages"] if m["role"] == "user"])
    
    question_categories = {"Chemistry": 0, "Bioinformatics": 0, "Compliance": 0, "Workflows": 0, "Other": 0}
    for m in ai_data["messages"]:
        if m["role"] == "user":
            content = m["content"].lower()
            if "compound" in content or "clogp" in content or "sar" in content or "drug" in content:
                question_categories["Chemistry"] += 1
            elif "sequence" in content or "egfr" in content or "mutation" in content or "mutant" in content:
                question_categories["Bioinformatics"] += 1
            elif "signature" in content or "compliance" in content or "audit" in content:
                question_categories["Compliance"] += 1
            elif "workflow" in content or "pipeline" in content:
                question_categories["Workflows"] += 1
            else:
                question_categories["Other"] += 1

    # 7. Metadata Calculations
    total_metadata_relationships = metadata_data["relationships_count"]
    total_metadata_fields = len(metadata_data["fields"])
    
    expected_values = len(metadata_data["entities"]) * total_metadata_fields
    actual_values = len(metadata_data["values"])
    metadata_completeness_score = round((actual_values / expected_values) * 100, 2) if expected_values > 0 else 0.0

    # 8. ELN/LIMS Calculations
    experiments_by_scientist = {}
    experiments_by_project = {}
    eln_lims_completed = 0
    eln_lims_total = 0

    for r in workflow_data["runs"]:
        wf_name = next((w["name"] for w in workflow_data["definitions"] if w["id"] == r["workflow_id"]), "")
        if "LIMS" in wf_name or "Assay Data Intake" in wf_name:
            eln_lims_total += 1
            if r["status"] == "COMPLETED":
                eln_lims_completed += 1
            
            wf_approvals = [app for app in workflow_data["approvals"] if app["run_id"] == r["id"]]
            for app in wf_approvals:
                scientist = app["approved_by"] or "Dr. Connor"
                experiments_by_scientist[scientist] = experiments_by_scientist.get(scientist, 0) + 1

    eln_lims_completion_rate = round((eln_lims_completed / eln_lims_total) * 100, 2) if eln_lims_total > 0 else 100.0

    # Compile the final aggregate payload
    return {
        "compounds": {
            "total_count": total_compounds,
            "by_target": compounds_by_target,
            "by_project": compounds_by_project,
            "mw_distribution": mw_values,
            "clogp_distribution": clogp_values,
            "hbd_distribution": hbd_values,
            "hba_distribution": hba_values,
            "lipinski_compliance": lipinski_compliance,
            "top_active": top_performing_compounds
        },
        "assays": {
            "total_count": total_assays,
            "by_target": assays_by_target,
            "ic50_distribution": ic50_values,
            "ec50_distribution": ec50_values,
            "success_rate": assay_success_rate,
            "top_performing": top_performing_compounds
        },
        "bioinformatics": {
            "total_count": total_sequences,
            "type_distribution": seq_type_dist,
            "organism_distribution": organism_dist,
            "mutation_frequency": mutation_count,
            "alignments_count": len(bioinfo_data["alignments"]),
            "clusters_count": len(bioinfo_data["clusters"])
        },
        "workflows": {
            "total_runs": total_workflows,
            "success_rate": workflow_success_rate,
            "failure_rate": workflow_failure_rate,
            "running_count": workflow_running_count,
            "avg_duration_sec": avg_workflow_duration,
            "sla_compliance_rate": workflow_sla_compliance_rate,
            "utilization": workflow_utilization,
            "steps": workflow_data["steps"],
            "approvals": workflow_data["approvals"]
        },
        "compliance": {
            "total_events": total_compliance_events,
            "events_by_type": audit_events_by_type,
            "events_by_user": audit_events_by_user,
            "signature_trends": signature_trends,
            "violations_count": compliance_violations,
            "health_score": compliance_health_score,
            "total_signatures": len(audit_data["signatures"]),
            "total_entity_versions": len(audit_data["entity_versions"])
        },
        "ai_copilot": {
            "total_sessions": total_chat_sessions,
            "total_messages": total_chat_messages,
            "total_queries": total_ai_queries,
            "question_categories": question_categories
        },
        "metadata": {
            "total_entities": len(metadata_data["entities"]),
            "total_fields": total_metadata_fields,
            "total_values": len(metadata_data["values"]),
            "total_relationships": total_metadata_relationships,
            "completeness_score": metadata_completeness_score
        },
        "eln_lims": {
            "experiments_by_scientist": experiments_by_scientist,
            "experiments_by_project": compounds_by_project,
            "completion_rate": eln_lims_completion_rate,
            "total_runs": eln_lims_total
        },
        "executive": {
            "total_assets": total_compounds + total_assays + total_sequences + total_workflows + total_compliance_events + total_ai_queries,
            "total_compounds": total_compounds,
            "total_assays": total_assays,
            "total_sequences": total_sequences,
            "total_workflows": total_workflows,
            "total_compliance_events": total_compliance_events,
            "total_ai_queries": total_ai_queries
        }
    }
