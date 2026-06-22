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
