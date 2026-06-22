# app/models/chemical.py
import os
import psycopg2
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.types import UserDefinedType
from app.core.database import Base

def check_rdkit_extension():
    # If the user explicitly disables the cartridge, or if no postgres DB is used
    if os.getenv("DISABLE_RDKIT_CARTRIDGE") == "1":
        return False
    db_url = os.getenv("DATABASE_URL")
    if not db_url or "postgresql" not in db_url:
        return False
    # Clean up trailing spaces if any
    db_url = db_url.strip()
    try:
        conn = psycopg2.connect(db_url, connect_timeout=3)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'rdkit'")
        exists = cur.fetchone() is not None
        cur.close()
        conn.close()
        return exists
    except Exception:
        return False

HAS_RDKIT = check_rdkit_extension()

class MolType(UserDefinedType):
    """
    Custom SQLAlchemy type mapping to the PostgreSQL RDKit Cartridge 'mol' type.
    """
    def get_col_spec(self, **kw):
        return "mol" if HAS_RDKIT else "VARCHAR"

class BfpType(UserDefinedType):
    """
    Custom SQLAlchemy type mapping to the PostgreSQL RDKit Cartridge 'bfp' type.
    """
    def get_col_spec(self, **kw):
        return "bfp" if HAS_RDKIT else "VARCHAR"

class Compound(Base):
    """
    SQLAlchemy Model representing the compounds table.
    RDKit molecular columns (mol and morgan_bfp) are updated automatically
    by DB-level triggers on SMILES writes.
    """
    __tablename__ = "compounds"
    __table_args__ = {"schema": "connector"}

    id = Column(Integer, primary_key=True, index=True)
    entity_key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    smiles = Column(String, nullable=False)
    mol = Column(MolType, nullable=True)
    morgan_bfp = Column(BfpType, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
