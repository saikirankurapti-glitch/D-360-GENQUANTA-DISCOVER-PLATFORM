from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Project(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None

class Experiment(BaseModel):
    experiment_id: str
    title: str
    project_id: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[str] = None
    status: Optional[str] = "Draft"

class Notebook(BaseModel):
    notebook_id: str
    name: str
    owner: Optional[str] = None
    created_at: Optional[str] = None

class Protocol(BaseModel):
    protocol_id: str
    name: str
    version: str
    description: Optional[str] = None

class Sample(BaseModel):
    sample_id: str
    batch_id: Optional[str] = None
    sample_type: str
    status: str
    amount_value: Optional[float] = None
    amount_unit: Optional[str] = None
    location: Optional[str] = None
    created_at: Optional[str] = None

class Plate(BaseModel):
    plate_id: str
    barcode: str
    plate_format: int = 384
    status: str

class Compound(BaseModel):
    compound_id: str
    name: str
    smiles: str
    mw: Optional[float] = None
    clogp: Optional[float] = None

class Assay(BaseModel):
    assay_id: str
    name: str
    target: Optional[str] = None
    assay_type: str

class Result(BaseModel):
    result_id: str
    assay_id: str
    compound_key: str
    activity_value: Optional[float] = None
    activity_unit: Optional[str] = None
    outcome: Optional[str] = None

class Instrument(BaseModel):
    instrument_id: str
    name: str
    type: str
    location: Optional[str] = None
    status: str

class Scientist(BaseModel):
    scientist_id: str
    name: str
    email: str
    department: Optional[str] = None
