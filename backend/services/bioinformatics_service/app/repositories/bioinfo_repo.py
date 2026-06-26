import json
import io
import numpy as np
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Align import PairwiseAligner
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from scipy.cluster.hierarchy import linkage
from sqlalchemy.orm import Session
from app.models.bioinfo import Sequence, SequenceVersion, SequenceAnnotation, Alignment, SequenceCluster
from app.schemas.bioinfo_schema import SequenceCreate, SequenceUpdate, PairwiseAlignmentRequest, SequenceClusterCreate, SearchSequenceRequest
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

# 1. Sequence Type Auto-detection
def detect_sequence_type(seq_str: str) -> str:
    seq_upper = seq_str.upper()
    # Check alphabet composition
    unique_chars = set(seq_upper)
    dna_chars = {'A', 'C', 'G', 'T', 'N'}
    rna_chars = {'A', 'C', 'G', 'U', 'N'}
    
    # If subset of DNA chars, it is DNA
    if unique_chars.issubset(dna_chars):
        return "DNA"
    elif unique_chars.issubset(rna_chars):
        return "RNA"
    return "Protein"

# 2. CRUD Operations
def create_sequence(db: Session, seq_in: SequenceCreate) -> Sequence:
    db_seq = Sequence(
        sequence_id=seq_in.sequence_id,
        name=seq_in.name,
        description=seq_in.description,
        sequence_type=seq_in.sequence_type,
        sequence_string=seq_in.sequence_string
    )
    db.add(db_seq)
    db.flush()

    if seq_in.annotations:
        for ann in seq_in.annotations:
            db_ann = SequenceAnnotation(
                sequence_id=db_seq.id,
                feature_type=ann.feature_type,
                start=ann.start,
                end=ann.end,
                strand=ann.strand or 1,
                name=ann.name,
                notes=ann.notes
            )
            db.add(db_ann)

    # Version 1 snapshot
    db_version = SequenceVersion(
        sequence_db_id=db_seq.id,
        version=1,
        sequence_string=seq_in.sequence_string,
        modified_by="system",
        change_summary="Initial import"
    )
    db.add(db_version)
    
    db.commit()
    db.refresh(db_seq)
    return db_seq

def get_sequences(db: Session, skip: int = 0, limit: int = 100) -> List[Sequence]:
    return db.query(Sequence).offset(skip).limit(limit).all()

def get_sequence_by_id(db: Session, seq_id: str) -> Optional[Sequence]:
    return db.query(Sequence).filter(Sequence.sequence_id == seq_id).first()

def get_sequence_by_db_id(db: Session, db_id: int) -> Optional[Sequence]:
    return db.query(Sequence).filter(Sequence.id == db_id).first()

# 3. FASTA Import
def import_fasta(db: Session, fasta_content: str) -> List[Sequence]:
    imported = []
    fasta_file = io.StringIO(fasta_content)
    for record in SeqIO.parse(fasta_file, "fasta"):
        seq_str = str(record.seq)
        seq_type = detect_sequence_type(seq_str)
        
        # Check if exists
        existing = get_sequence_by_id(db, record.id)
        if existing:
            # Update sequence string & increment version
            existing.sequence_string = seq_str
            existing.sequence_type = seq_type
            db.flush()
            
            # Fetch latest version num
            last_ver = db.query(SequenceVersion).filter(SequenceVersion.sequence_db_id == existing.id).order_by(SequenceVersion.version.desc()).first()
            new_ver_num = (last_ver.version + 1) if last_ver else 1
            
            db_version = SequenceVersion(
                sequence_db_id=existing.id,
                version=new_ver_num,
                sequence_string=seq_str,
                modified_by="system",
                change_summary=f"Updated via FASTA re-import"
            )
            db.add(db_version)
            db.commit()
            db.refresh(existing)
            imported.append(existing)
        else:
            # Create new
            seq_in = SequenceCreate(
                sequence_id=record.id,
                name=record.name or record.id,
                description=record.description,
                sequence_type=seq_type,
                sequence_string=seq_str
            )
            new_seq = create_sequence(db, seq_in)
            imported.append(new_seq)
            
    return imported

# 4. Protein Analytics calculations
def calculate_protein_metrics(seq_str: str) -> Dict[str, Any]:
    # Clean sequence of non-standard chars just in case
    cleaned_seq = "".join([c for c in seq_str.upper() if c in "ACDEFGHIKLMNPQRSTVWY"])
    if len(cleaned_seq) == 0:
        return {
            "molecular_weight": 0.0,
            "isoelectric_point": 7.0,
            "gravy": 0.0,
            "composition": {}
        }
    
    analysis = ProteinAnalysis(cleaned_seq)
    try:
        mw = analysis.molecular_weight()
        pi = analysis.isoelectric_point()
        gravy = analysis.gravy()
        comp = analysis.count_amino_acids()
    except Exception:
        mw = 0.0
        pi = 7.0
        gravy = 0.0
        comp = {}

    return {
        "molecular_weight": float(mw),
        "isoelectric_point": float(pi),
        "gravy": float(gravy),
        "composition": comp
    }

# 5. Pairwise Sequence Alignment
def run_pairwise_alignment(req: PairwiseAlignmentRequest, seq_a: str, seq_b: str) -> Dict[str, Any]:
    aligner = PairwiseAligner()
    aligner.mode = req.alignment_type # global or local
    aligner.match_score = req.match_score
    aligner.mismatch_score = req.mismatch_score
    aligner.open_gap_score = req.open_gap_score
    aligner.extend_gap_score = req.extend_gap_score

    alignments = aligner.align(seq_a, seq_b)
    try:
        best_alignment = alignments[0]
    except (IndexError, OverflowError):
        return {"score": 0.0, "aligned_a": seq_a, "aligned_b": seq_b, "visualization": ""}
    
    # Generate visualization/string representation
    aligned_a, aligned_b = best_alignment[0], best_alignment[1]
    
    return {
        "score": float(best_alignment.score),
        "aligned_a": aligned_a,
        "aligned_b": aligned_b,
        "visualization": str(best_alignment)
    }

# 6. Progressive MSA & Consensus Alignment
def run_multiple_alignment(sequences: List[Tuple[str, str]]) -> Dict[str, Any]:
    """
    Performs progressive alignment in Python by anchoring other sequences to the longest sequence.
    Returns aligned sequences list, Clustal output format, and Consensus sequence.
    """
    if not sequences:
        return {"clustal": "", "consensus": "", "aligned": {}}
        
    # Sort sequences by length descending
    sorted_seqs = sorted(sequences, key=lambda x: len(x[1]), reverse=True)
    anchor_id, anchor_seq = sorted_seqs[0]
    
    aligned_results = {anchor_id: anchor_seq}
    
    # We will align all other sequences to the anchor
    aligner = PairwiseAligner()
    aligner.mode = 'global'
    
    for seq_id, seq_str in sorted_seqs[1:]:
        alignments = aligner.align(anchor_seq, seq_str)
        if alignments:
            best_align = alignments[0]
            # Extract alignment representation
            aligned_anchor = best_align[0]
            aligned_other = best_align[1]
            
            # Since anchor sequence may now have gaps in this alignment, we propagate gaps
            # to keep everything in sync relative to the original anchor!
            aligned_results[seq_id] = aligned_other
            # Update anchor sequence to include gaps if necessary
            # For simplicity in output, we padding/gap fill each to the max length of aligned anchor
            if len(aligned_other) > len(anchor_seq):
                aligned_results[anchor_id] = aligned_anchor
        else:
            aligned_results[seq_id] = seq_str

    # Pad all aligned sequences to equal length
    max_len = max(len(s) for s in aligned_results.values())
    for seq_id in aligned_results:
        s = aligned_results[seq_id]
        if len(s) < max_len:
            aligned_results[seq_id] = s + "-" * (max_len - len(s))

    # Generate Consensus
    consensus_list = []
    clustal_lines = ["CLUSTAL W multiple sequence alignment\n\n"]
    
    for idx in range(max_len):
        column_chars = [aligned_results[s_id][idx] for s_id in aligned_results]
        # Find mode (most common char)
        char_counts = {}
        for c in column_chars:
            if c != '-':
                char_counts[c] = char_counts.get(c, 0) + 1
        
        best_char = '-'
        if char_counts:
            best_char = max(char_counts, key=char_counts.get)
        consensus_list.append(best_char)

    consensus_str = "".join(consensus_list)

    # Format Clustal
    for seq_id, val in aligned_results.items():
        clustal_lines.append(f"{seq_id[:15]:<16} {val}\n")
    clustal_lines.append(f"{'consensus':<16} {consensus_str}\n")
    
    return {
        "clustal": "".join(clustal_lines),
        "consensus": consensus_str,
        "aligned": aligned_results
    }

# 7. Motif Search, Exact Match, Similarity
def search_sequence(db: Session, req: SearchSequenceRequest) -> List[Dict[str, Any]]:
    sequences = db.query(Sequence).all()
    results = []
    
    query = req.query_string.upper()
    
    for s in sequences:
        s_str = s.sequence_string.upper()
        if req.search_type == "exact":
            if query in s_str:
                results.append({
                    "sequence_id": s.sequence_id,
                    "name": s.name,
                    "type": s.sequence_type,
                    "matches": [i for i in range(len(s_str)) if s_str.startswith(query, i)]
                })
        elif req.search_type == "motif":
            # Motif search: simple regex matching or character matching
            # Let's import standard re for motif regex matching!
            import re
            try:
                # Convert standard amino acid/nucleotide motifs if necessary, or compile directly
                matches = [m.start() for m in re.finditer(query, s_str)]
                if matches:
                    results.append({
                        "sequence_id": s.sequence_id,
                        "name": s.name,
                        "type": s.sequence_type,
                        "matches": matches
                    })
            except Exception:
                pass
        else: # similarity
            # Compute quick Jaccard or alignment identity
            intersect = len(set(query) & set(s_str))
            union = len(set(query) | set(s_str))
            score = intersect / union if union > 0 else 0.0
            
            if score >= (req.threshold or 0.7):
                results.append({
                    "sequence_id": s.sequence_id,
                    "name": s.name,
                    "type": s.sequence_type,
                    "score": round(score, 3)
                })
    return results

# 8. Hierarchical Clustering & Distance Matrix
def perform_clustering(db: Session, req: SequenceClusterCreate) -> SequenceCluster:
    db_seqs = db.query(Sequence).filter(Sequence.sequence_id.in_(req.seq_ids)).all()
    if len(db_seqs) < 2:
        raise ValueError("At least 2 sequences are required for clustering.")

    # Calculate distance matrix (1.0 - identity fraction)
    n = len(db_seqs)
    dist_matrix = np.zeros((n, n))
    aligner = PairwiseAligner()
    aligner.mode = 'global'

    for i in range(n):
        for j in range(i + 1, n):
            seq_a = db_seqs[i].sequence_string
            seq_b = db_seqs[j].sequence_string
            
            alignments = aligner.align(seq_a, seq_b)
            if alignments:
                best = alignments[0]
                # Identity score = matches / max(length_a, length_b)
                matches = best.score
                max_len = max(len(seq_a), len(seq_b))
                identity = matches / max_len if max_len > 0 else 0.0
                dist = 1.0 - identity
            else:
                dist = 1.0
                
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist

    # Prepare condensed matrix for SciPy linkage
    condensed_dist = []
    for i in range(n):
        for j in range(i + 1, n):
            condensed_dist.append(dist_matrix[i, j])

    # Run linkage
    Z = linkage(condensed_dist, method='average') # UPGMA

    # Save to db
    matrix_data = {
        "labels": [s.sequence_id for s in db_seqs],
        "values": dist_matrix.tolist()
    }
    
    db_cluster = SequenceCluster(
        name=req.name,
        method=req.method,
        distance_metric=req.distance_metric,
        matrix_json=json.dumps(matrix_data),
        linkage_json=json.dumps(Z.tolist())
    )
    db.add(db_cluster)
    db.commit()
    db.refresh(db_cluster)
    return db_cluster
