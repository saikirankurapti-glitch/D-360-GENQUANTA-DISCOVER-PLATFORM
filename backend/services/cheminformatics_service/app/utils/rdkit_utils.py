# app/utils/rdkit_utils.py
from typing import Dict, Any, List, Optional
import binascii
from rdkit import Chem, DataStructs, RDLogger
RDLogger.DisableLog('rdApp.*')
from rdkit.Chem import Descriptors, Lipinski, Draw, rdMolDescriptors
from rdkit.Chem.rdRGroupDecomposition import RGroupDecompose, RGroupDecomposition, RGroupDecompositionParameters

def validate_and_canonicalize_smiles(smiles: str) -> Optional[str]:
    """
    Validates a SMILES string and returns its canonicalized representation.
    Returns None if the SMILES string is invalid.
    """
    if not smiles or not smiles.strip():
        return None
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol, canonical=True)
    except Exception:
        return None

def calculate_descriptors(smiles: str) -> Optional[Dict[str, Any]]:
    """
    Calculates key chemical descriptors and properties for a given SMILES.
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        
        # Calculate properties using RDKit modules
        properties = {
            "mw": float(Descriptors.ExactMolWt(mol)),
            "logp": float(Descriptors.MolLogP(mol)),
            "tpsa": float(Descriptors.TPSA(mol)),
            "hbd": int(Lipinski.NumHDonors(mol)),
            "hba": int(Lipinski.NumHAcceptors(mol)),
            "rotatable_bonds": int(Lipinski.NumRotatableBonds(mol)),
            "formula": rdMolDescriptors.CalcMolFormula(mol),
            "heavy_atoms": int(mol.GetNumHeavyAtoms())
        }
        return properties
    except Exception as e:
        print(f"Error calculating descriptors: {e}")
        return None

def generate_fingerprint_hex(smiles: str, radius: int = 2, n_bits: int = 2048) -> Optional[str]:
    """
    Generates a Morgan fingerprint (Circular/ECFP equivalent) as a hex string.
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        
        # Morgan fingerprint generator
        fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
        # Convert bit vector to binary bytes, then convert to hex string
        return binascii.hexlify(DataStructs.BitVectToBinaryText(fp)).decode('utf-8')
    except Exception as e:
        print(f"Error generating fingerprint: {e}")
        return None

def draw_molecule_svg(smiles: str, size: int = 300) -> Optional[str]:
    """
    Generates a high-quality SVG image string representing the structure of the molecule.
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        
        # Standardize 2D coordinates for drawing
        Chem.rdDepictor.Compute2DCoords(mol)
        
        # Set drawing options
        drawer = Draw.rdMolDraw2D.MolDraw2DSVG(size, size)
        options = drawer.drawOptions()
        options.clearBackground = True
        
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        
        return drawer.GetDrawingText()
    except Exception as e:
        print(f"Error drawing molecule: {e}")
        return None

def perform_sar_analysis(
    compounds: List[Dict[str, Any]], 
    scaffold_smiles: str
) -> Optional[Dict[str, Any]]:
    """
    Performs Structure-Activity Relationship (SAR) analysis.
    Decomposes compounds into R-groups based on a shared core scaffold.
    
    compounds: List of dicts, each with keys 'smiles' and 'activity' (numeric value like IC50/EC50)
    scaffold_smiles: Shared core/scaffold structure
    """
    try:
        core = Chem.MolFromSmiles(scaffold_smiles)
        if core is None:
            raise ValueError("Invalid core scaffold SMILES")
            
        # Parse molecules
        mols = []
        activities = []
        names = []
        for idx, item in enumerate(compounds):
            mol = Chem.MolFromSmiles(item['smiles'])
            if mol is not None:
                mols.append(mol)
                activities.append(item.get('activity', 0.0))
                names.append(item.get('name', f"Comp-{idx+1}"))
                
        if not mols:
            return {"error": "No valid molecules provided for decomposition."}
            
        # Run R-Group Decomposition
        params = RGroupDecompositionParameters()
        rgd = RGroupDecomposition(core, params)
        
        for mol in mols:
            rgd.Add(mol)
            
        rgd.Process()
        
        # Format results
        rows = rgd.GetRGroupsAsRows()
        if not rows:
            return {"scaffold": scaffold_smiles, "compounds": [], "activity_cliffs": []}
            
        columns = list(rows[0].keys()) # Core, R1, R2, etc.
        
        results = []
        for idx, row in enumerate(rows):
            comp_res = {
                "name": names[idx],
                "smiles": compounds[idx]['smiles'],
                "activity": activities[idx],
                "r_groups": {}
            }
            # Convert R-group molecule objects to SMILES strings
            for col in columns:
                if col == "Core":
                    comp_res["core_smiles"] = Chem.MolToSmiles(row[col])
                else:
                    comp_res["r_groups"][col] = Chem.MolToSmiles(row[col])
            results.append(comp_res)
            
        # Compute dynamic activity cliffs (compounds differing by a single R-group but showing large activity shifts)
        cliffs = []
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                res_i = results[i]
                res_j = results[j]
                
                # Check if core is same and they have the exact same columns of R-groups
                r_i = res_i["r_groups"]
                r_j = res_j["r_groups"]
                
                if r_i.keys() != r_j.keys():
                    continue
                    
                # Find number of differing R-groups
                diff_count = 0
                diff_r_group = ""
                for key in r_i:
                    if r_i[key] != r_j[key]:
                        diff_count += 1
                        diff_r_group = key
                        
                # If they differ by exactly one R-group (Matched Molecular Pair)
                if diff_count == 1:
                    activity_ratio = 0.0
                    if min(res_i["activity"], res_j["activity"]) > 0:
                        activity_ratio = max(res_i["activity"], res_j["activity"]) / min(res_i["activity"], res_j["activity"])
                    else:
                        activity_ratio = abs(res_i["activity"] - res_j["activity"])
                        
                    # High cliff threshold (e.g. > 10-fold change or > 1.5 units)
                    if activity_ratio >= 10.0 or (activity_ratio > 1.5 and min(res_i["activity"], res_j["activity"]) == 0):
                        cliffs.append({
                            "compound_a": res_i["name"],
                            "compound_b": res_j["name"],
                            "differing_r_group": diff_r_group,
                            "group_a": r_i[diff_r_group],
                            "group_b": r_j[diff_r_group],
                            "activity_a": res_i["activity"],
                            "activity_b": res_j["activity"],
                            "activity_ratio": activity_ratio
                        })
                        
        return {
            "scaffold": scaffold_smiles,
            "compounds": results,
            "activity_cliffs": cliffs
        }
    except Exception as e:
        print(f"Error in SAR analysis: {e}")
        return {"error": str(e)}
