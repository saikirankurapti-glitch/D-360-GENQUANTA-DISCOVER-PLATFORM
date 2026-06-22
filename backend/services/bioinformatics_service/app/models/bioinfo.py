from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Sequence(Base):
    __tablename__ = "sequences"
    __table_args__ = {"schema": "bio"}

    id = Column(Integer, primary_key=True, index=True)
    sequence_id = Column(String, unique=True, index=True, nullable=False) # e.g. Accession key
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    sequence_type = Column(String, nullable=False) # DNA, RNA, Protein
    sequence_string = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    versions = relationship("SequenceVersion", back_populates="sequence", cascade="all, delete-orphan")
    annotations = relationship("SequenceAnnotation", back_populates="sequence", cascade="all, delete-orphan")


class SequenceVersion(Base):
    __tablename__ = "sequence_versions"
    __table_args__ = {"schema": "bio"}

    id = Column(Integer, primary_key=True, index=True)
    sequence_db_id = Column(Integer, ForeignKey("bio.sequences.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    sequence_string = Column(Text, nullable=False)
    modified_by = Column(String, nullable=False)
    modified_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    change_summary = Column(String, nullable=True)

    sequence = relationship("Sequence", back_populates="versions")


class SequenceAnnotation(Base):
    __tablename__ = "sequence_annotations"
    __table_args__ = {"schema": "bio"}

    id = Column(Integer, primary_key=True, index=True)
    sequence_id = Column(Integer, ForeignKey("bio.sequences.id", ondelete="CASCADE"), nullable=False)
    feature_type = Column(String, nullable=False) # gene, promoter, exon, binding_site
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)
    strand = Column(Integer, default=1, nullable=False) # 1 or -1
    name = Column(String, nullable=False)
    notes = Column(Text, nullable=True)

    sequence = relationship("Sequence", back_populates="annotations")


class Alignment(Base):
    __tablename__ = "alignments"
    __table_args__ = {"schema": "bio"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    alignment_type = Column(String, nullable=False) # pairwise_global, pairwise_local, multiple
    sequences_metadata = Column(Text, nullable=True) # json list of sequence IDs in order
    alignment_data = Column(Text, nullable=False) # clustal or aligned fasta format
    score = Column(Float, nullable=True)
    consensus = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SequenceCluster(Base):
    __tablename__ = "sequence_clusters"
    __table_args__ = {"schema": "bio"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    method = Column(String, nullable=False) # hierarchical, UPGMA, etc.
    distance_metric = Column(String, nullable=False) # identity, blosum62, Jukes-Cantor
    matrix_json = Column(Text, nullable=False) # JSON encoded matrix
    linkage_json = Column(Text, nullable=False) # JSON encoded linkage array
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
