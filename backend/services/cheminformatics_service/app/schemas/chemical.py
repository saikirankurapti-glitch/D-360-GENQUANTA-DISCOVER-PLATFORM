from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Dict, Optional, Any
from datetime import datetime
from app.utils.rdkit_utils import validate_and_canonicalize_smiles

# Compound Schemas
class CompoundBase(BaseModel):
    entity_key: str = Field(..., description="Unique alphanumeric identifier for the compound")
    name: str = Field(..., description="Common or IUPAC name of the compound")
    smiles: str = Field(..., description="SMILES string representation of the molecule")

    @field_validator('smiles')
    @classmethod
    def check_smiles_validity(cls, v: str) -> str:
        canonical = validate_and_canonicalize_smiles(v)
        if canonical is None:
            raise ValueError("Provided SMILES is chemically invalid or cannot be parsed by RDKit")
        return canonical

class CompoundCreate(CompoundBase):
    pass

class CompoundResponse(CompoundBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Search Schemas
class SearchResult(BaseModel):
    id: int
    entity_key: str
    name: str
    smiles: str
    similarity: Optional[float] = Field(None, description="Tanimoto similarity score (only populated for similarity searches)")

# Descriptor Schemas
class DescriptorResponse(BaseModel):
    smiles: str
    mw: float = Field(..., description="Exact Molecular Weight")
    logp: float = Field(..., description="Calculated logP (octanol-water partition coefficient)")
    tpsa: float = Field(..., description="Topological Polar Surface Area")
    hbd: int = Field(..., description="Number of Hydrogen Bond Donors")
    hba: int = Field(..., description="Number of Hydrogen Bond Acceptors")
    rotatable_bonds: int = Field(..., description="Number of Rotatable Bonds")
    formula: str = Field(..., description="Molecular Formula")
    heavy_atoms: int = Field(..., description="Number of Heavy Atoms")

# Fingerprint Schemas
class FingerprintResponse(BaseModel):
    smiles: str
    fingerprint_hex: str = Field(..., description="Morgan fingerprint represented as a hexadecimal string")

# SAR (Structure-Activity Relationship) Schemas
class CompoundActivity(BaseModel):
    smiles: str = Field(..., description="SMILES representation of analogue molecule")
    activity: float = Field(..., description="Activity value (e.g. IC50, pIC50, % inhibition)")
    name: Optional[str] = Field(None, description="Optional label for the analogue")

    @field_validator('smiles')
    @classmethod
    def check_smiles_validity(cls, v: str) -> str:
        canonical = validate_and_canonicalize_smiles(v)
        if canonical is None:
            raise ValueError("Provided analogue SMILES is chemically invalid")
        return canonical

class SARRequest(BaseModel):
    compounds: List[CompoundActivity] = Field(..., description="List of analogues with activity data")
    scaffold_smiles: str = Field(..., description="SMILES representation of core scaffold")

    @field_validator('scaffold_smiles')
    @classmethod
    def check_scaffold_validity(cls, v: str) -> str:
        canonical = validate_and_canonicalize_smiles(v)
        if canonical is None:
            raise ValueError("Provided core scaffold SMILES is chemically invalid")
        return canonical

class SARCliff(BaseModel):
    compound_a: str
    compound_b: str
    differing_r_group: str
    group_a: str
    group_b: str
    activity_a: float
    activity_b: float
    activity_ratio: float

class SARAnalogueResult(BaseModel):
    name: str
    smiles: str
    activity: float
    core_smiles: str
    r_groups: Dict[str, str]

class SARResponse(BaseModel):
    scaffold: str
    compounds: List[SARAnalogueResult]
    activity_cliffs: List[SARCliff]
