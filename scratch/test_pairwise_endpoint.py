from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys

# Add bioinformatics service to python path
sys.path.append(r"c:\Users\saiki\GENQUANTAA DISCOVER\backend\services\bioinformatics_service")

from app.core.database import Base
from app.repositories import bioinfo_repo
from app.schemas.bioinfo_schema import PairwiseAlignmentRequest

# Connect to database
engine = create_engine("postgresql://postgres:Saikiran%40123@localhost:5432/genquantaa_bioinfo")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Get two sequences from the DB
seqs = bioinfo_repo.get_sequences(db, limit=2)
print("Found sequences:", [s.sequence_id for s in seqs])

if len(seqs) >= 2:
    req = PairwiseAlignmentRequest(
        seq_a_id=seqs[0].sequence_id,
        seq_b_id=seqs[1].sequence_id,
        alignment_type="global",
        match_score=1.0,
        mismatch_score=-1.0,
        open_gap_score=-0.5,
        extend_gap_score=-0.1
    )
    try:
        res = bioinfo_repo.run_pairwise_alignment(req, seqs[0].sequence_string, seqs[1].sequence_string)
        print("Success:", res["score"])
    except Exception as e:
        import traceback
        traceback.print_exc()

db.close()
