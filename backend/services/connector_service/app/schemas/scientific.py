from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import date, datetime

class Project(BaseModel):
    project_id: str = Field(..., description="Unique identifier for the project")
    name: str = Field(..., description="Display name of the project")
    description: Optional[str] = Field(None, description="Detailed description")
    created_at: Optional[date] = None

class Experiment(BaseModel):
    experiment_id: str = Field(..., description="Unique notebook entry ID")
    title: str = Field(..., description="Title of the experiment")
    project_name: Optional[str] = Field(None, description="Associated project name")
    author: Optional[str] = Field(None, description="Experiment author")
    created_date: date = Field(..., description="Creation date")
    status: Optional[str] = Field("Draft", description="State (Draft, In Progress, Signed Off)")

class Protocol(BaseModel):
    protocol_id: str = Field(..., description="Unique protocol template ID")
    name: str = Field(..., description="Protocol standard name")
    version: str = Field("1.0", description="Protocol version number")
    description: Optional[str] = None

class Sample(BaseModel):
    sample_id: str = Field(..., description="Unique sample barcode or ID")
    batch_id: Optional[str] = Field(None, description="Parent compound batch identifier")
    sample_type: str = Field(..., description="e.g. DNA, Protein, Blood Serum, Compound Powder")
    status: str = Field("Logged", description="LIMS inventory status")
    amount_value: Optional[float] = Field(None, description="Available quantity value")
    amount_unit: Optional[str] = Field(None, description="Available quantity unit")
    location: Optional[str] = Field(None, description="Storage location (e.g. Freezer-3, Shelf-B)")
    created_at: Optional[date] = None

class Plate(BaseModel):
    plate_id: str = Field(..., description="Unique barcode of the assay/screening plate")
    barcode: str = Field(..., description="Readable plate barcode")
    plate_format: int = Field(96, description="Number of wells: 96, 384, etc.")
    status: str = Field("Empty", description="Plate workflow status")

class Assay(BaseModel):
    assay_id: str = Field(..., description="Unique screening assay configuration ID")
    name: str = Field(..., description="Assay assay catalog name")
    target: Optional[str] = Field(None, description="Target biological entity or protein (e.g. EGFR)")
    assay_type: str = Field(..., description="e.g. Enzymatic, HTRF, Cellular, Cardiotox")

class Result(BaseModel):
    result_id: str = Field(..., description="Individual test result record ID")
    assay_id: str = Field(..., description="Assay ID association")
    compound_key: str = Field(..., description="Chemical compound key (e.g. CHEM-0012)")
    activity_value: Optional[float] = Field(None, description="Activity raw value (e.g. IC50, Inhibition)")
    activity_unit: Optional[str] = Field(None, description="Units (e.g. uM, %)")
    outcome: Optional[str] = Field(None, description="Screen outcome: Active, Inactive, Inconclusive")
    run_date: Optional[date] = None
