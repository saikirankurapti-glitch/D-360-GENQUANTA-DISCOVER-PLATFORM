import psycopg2
import json
import random
import hashlib
from datetime import datetime, timedelta

# Try to import RDKit for high-fidelity chemical property calculations
try:
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors
    HAS_RDKIT = True
    print("Python RDKit package detected. Enabling chemical property calculations...")
except ImportError:
    HAS_RDKIT = False
    print("Python RDKit package NOT detected. Using fallback mock calculations...")

# Database connection details
DB_USER = "postgres"
DB_PASS = "Saikiran@123"
DB_HOST = "localhost"
DB_PORT = "5432"

DATABASES = {
    "auth": "genquantaa_auth",
    "metadata": "genquantaa_metadata",
    "query": "genquantaa_query",
    "chem": "cheminformatics",
    "connector": "genquantaa_connector",
    "audit": "genquantaa_audit",
    "lineage": "genquantaa_lineage",
    "bio": "genquantaa_bioinfo",
    "workflow": "genquantaa_workflow",
    "ai": "genquantaa_ai"
}

def get_connection(db_key):
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DATABASES[db_key]
    )

# =====================================================================
# CHEMICAL DATA GENERATOR (500+ Compounds)
# =====================================================================
def generate_compounds(count=550):
    scaffolds = [
        "c1ccccc1", # benzene
        "c1ccncc1", # pyridine
        "c1cnc2c(c1)cc(cc2)N", # quinoline
        "O=C(Nc1ccccc1)c2ccccc2", # benzanilide
        "O=C(Nc1ccc(F)cc1)c2ccc(C(=O)NCC3CC3)cc2", # kinase inhibitor scaffold
        "c1cc2c(cc1F)c(c3ccccc3)n(n2)C", # indazole
        "Cc1ccccc1", # toluene
        "Oc1ccccc1", # phenol
        "c1cc(cc(c1)Cl)C", # chlorotoluene
        "CCN(CC)c1ccc(c2ccccc2)cc1", # tertiary amine
    ]
    # Fixed R-groups: Avoid digits like '3' in CF3 and '2' in NO2 since SMILES parses digits as ring endpoints!
    r_groups = [
        "F", "Cl", "Br", "C", "OC", "O", "N", "C(F)(F)F", "C(=O)N", "S(=O)(=O)C", "CC", "OCC", "N(=O)=O", "CN"
    ]
    
    drugs = [
        ("Gefitinib", "COc1cc2c(Nc3ccc(Cl)c(F)c3)c(CN4CCOCC4)cnc2cc1OC"),
        ("Erlotinib", "COCCOc1cc2c(Nc3cccc(C#C)c3)ncnc2cc1OCCOC"),
        ("Lapatinib", "CS(=O)(=O)CCNc1ccc2ccc(Nc3ccc(OCc4cccc(F)c4)c(Cl)c3)ncnc2c1"),
        ("Sorafenib", "CNC(=O)c1cc(Oc2ccc(NC(=O)Nc3ccc(Cl)c(C(F)(F)F)c3)cc2)ccn1"),
        ("Imatinib", "Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc4nccc(c5cccnc5)n4"),
        ("Vemurafenib", "CCCS(=O)(=O)Nc1ccc(F)c(C(=O)c2c[nH]c3ccc(Cl)cn23)c1F"),
        ("Aspirin", "CC(=O)Oc1ccccc1C(=O)O"),
        ("Paracetamol", "CC(=O)Nc1ccc(O)cc1"),
        ("Ibuprofen", "CC(C)Cc1ccc(cc1)C(C)C(=O)O"),
        ("Caffeine", "CN1C=NC2=C1C(=O)N(C)C(=O)N2C"),
    ]
    
    compounds = []
    
    # Add seed drug compounds first
    for idx, (name, smiles) in enumerate(drugs):
        compounds.append({
            "entity_key": f"CMP-{idx+1:05d}",
            "name": name,
            "smiles": smiles
        })
        
    # Generate variations
    scaffold_idx = 0
    while len(compounds) < count:
        scaffold = scaffolds[scaffold_idx % len(scaffolds)]
        r1 = r_groups[(scaffold_idx * 7) % len(r_groups)]
        r2 = r_groups[(scaffold_idx * 13) % len(r_groups)]
        
        # Build substituted molecule
        if HAS_RDKIT:
            try:
                # Add substituents in a chemically valid way
                if "=" in scaffold:
                    sm = f"O=C(Nc1ccc({r1})cc1)c2ccc({r2})cc2"
                else:
                    sm = f"Oc1cc({r1})c({r2})cc1"
                
                mol = Chem.MolFromSmiles(sm)
                if mol:
                    canonical_smiles = Chem.MolToSmiles(mol)
                    compounds.append({
                        "entity_key": f"CMP-{len(compounds)+1:05d}",
                        "name": f"Kinase Inhibitor Derivative Gen-{len(compounds)+1}",
                        "smiles": canonical_smiles
                    })
            except Exception:
                pass
        else:
            # Fallback if RDKit is not available
            compounds.append({
                "entity_key": f"CMP-{len(compounds)+1:05d}",
                "name": f"Kinase Inhibitor Derivative Gen-{len(compounds)+1}",
                "smiles": f"CC(=O)Nc1ccc(O)cc1C({r1})({r2})"
            })
            
        scaffold_idx += 1
        
    return compounds

def calculate_chemical_properties(smiles):
    if HAS_RDKIT:
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                return {
                    "mw": float(rdMolDescriptors.CalcExactMolWt(mol)),
                    "clogp": float(rdMolDescriptors.CalcCrippenDescriptors(mol)[0]),
                    "hbd": int(rdMolDescriptors.CalcNumLipinskiHBD(mol)),
                    "hba": int(rdMolDescriptors.CalcNumLipinskiHBA(mol)),
                    "tpsa": float(rdMolDescriptors.CalcTPSA(mol)),
                    "rotatable_bonds": int(rdMolDescriptors.CalcNumRotatableBonds(mol)),
                    "formula": str(rdMolDescriptors.CalcMolFormula(mol)),
                    "heavy_atoms": int(mol.GetNumHeavyAtoms())
                }
        except Exception:
            pass
            
    # Fallback properties
    return {
        "mw": round(random.uniform(200.0, 600.0), 2),
        "clogp": round(random.uniform(-1.0, 6.0), 3),
        "hbd": random.randint(0, 5),
        "hba": random.randint(1, 10),
        "tpsa": round(random.uniform(30.0, 150.0), 1),
        "rotatable_bonds": random.randint(0, 10),
        "formula": "C20H25N3O3S",
        "heavy_atoms": random.randint(15, 45)
    }

# =====================================================================
# BIOINFORMATICS FASTA GENERATOR (100+ Sequences)
# =====================================================================
def generate_sequences(count=110):
    sequence_types = ["Protein", "DNA", "RNA"]
    targets = ["EGFR", "HER2", "BRAF", "BCR-ABL", "ALK", "PD-1", "KRAS", "TP53"]
    
    # Real base sequence fragments
    base_protein = "MRPSGTAGAALLALLAALCPASRALEEKKVCQGTSNKLTQLGTFEDHFLSLQRMFNNCEVVLGNLEITYVQRNYDLSFLKTIQEVAGYVLIALNTVERIPLENLQIIRGNMYYENSYALAVLSNYDANKTGLKELPMRNLQEILHGAVRFSNNPALCNVESIQWRDIVSSDFLSNMSMDFQNHLGSCQKCDPSCPNGSCWGAGEENCQKLTKIICAQQCSGRCRGKSPSDCCHNQCAAGCTGPRESDCLVCRKFRDEATCKDTCPPLMLYNPTTYQMDVNPEGKYSFGATCVKKCPRNYVVTDHGSCVRACGADSYEMEEDGVRKCKKCEGPCRKVCNGIGIGEFKDSLSINATNIKHFKNCTSISGDLHILPVAFRGDSFTHTPPLDPQELDILKTVKEITGFLLIQAWPENRTDLHAFENLEIIRGRTKQHGQFSLAVVSLNITSLGLRSLKEISDGDVIISGNKNLCYANTINWKKLFGTSGQKTKIISNRGENSCKATGQVCHALCSPEGCWGPEPRDCVSCRNVSRGRECVDKCNLLEGEPREFVENSECIQCHPECLPQAMNITCTGRGPDNCIQCAHYIDGPHCVKTCPAGVMGENNTLVWKYADAGHVCHLCHPNCTYGCTGPGLEGCPTNGPKIPSIATGMVGALLLLLVVALGIGLFMRRRHIVRKRTLRRLLQERELVEPLTPSGEAPNQALLRILKETEFKKIKVLGSGAFGTVYKGLWIPEGEKVKIPVAIKELREATSPKANKEILDEAYVMASVDNPHVCRLLGICLTSTVQLITQLMPFGCLLDYVREHKDNIGSQYLLNWCVQIAKGMNYLEDRRLVHRDLAARNVLVKTPQHVKITDFGLAKLLGAEEKEYHAEGGKVPIKWMALESILHRIYTHQSDVWSYGVTVWELMTFGSKPYDGIPASEISSILEKGERLPQPPICTIDVYMIMVKCWMIDADSRPKFRELIIEFSKMARDPQRYLVIQGDERMHLPSPTDSNFYRALMDEEDMDDVVDADEYLIPQQGFFSSPSTSRTPLLSSLSATSNNSTVACIDRNGLQSCPIKEDSFLQRYSSDPTGALTEDSIDDTFLPVPEYINQSVPKRPAGSVQNPVYHNQPLNPAPSRDPHYQDPHSTAVGNPEYLNTVQPTCVNSTFDSPAHWAQKGSHQISLDNPDYQQDFFPKEAKPNGIFKGSTAENAEYLRVAPQSSEFIGA"
    base_dna = "ATGCGACCCTCCGGGACGGCCGGGGCAGCGCTCCTGGCGCTGCTGGCTGCGCTCTGCCCGGCGAGTCGGGCTCTGGAGGAAAAGAAAGTTTGCCAAGGCACGAGTAACAAGCTCACGCAGTTGGGCACTTTTGAAGATCATTTTCTCAGCCTCCAGAGGATGTTCAATAACTGTGAGGTGGTCCTTGGGAATTTGGAAATTACCTATGTGCAGAGGAATTATGATCTTTCCTTCTTAAAGACCATCCAGGAGGTGGCTGGTTATGTCCTCATTGCCCTCAACACAGTGGAGCGAATCCCTTTGGAAAACCTGCAGATCATCAGAGGAAATATGTACTACGAAAATTCCTATGCCTTAGCAGTCTTATCTAACTATGATGCAAATAAAACCGGACTGAAGGAGCTGCCCATGAGAAATTTACAGGAAATCCTGCATGGCGCCGTGCGGTTCAGCAACAACCCTGCCCTGTGCAACGTGGAGAGCATCCAGTGGCGGGACATAGTCAGCAGTGACTTTCTCAGCAACATGTCGATGGACTTCCAGAACCACCTGGGCAGCTGCCAAAAGTGTGATCCAAGCTGTCCCAATGGGAGCTGCTGGGGTGCAGGAGAGGAGAACTGCCAGAAACTGACCAAAATCATCTGTGCCCAGCAGTGCTCCGGGCGCTGCCGTGGCAAGTCCCCCAGTGACTGCTGCCACAACCAGTGTGCTGCAGGCTGCACGGGCCCCCGGGAGAGCGACTGCCTGGTCTGCCGCAAATTCCGAGACGAAGCCACGTGCAAGGACACCTGCCCCCCACTCATGCTCTACAACCCCACCACGTACCAGATGGATGTGAACCCCGAGGGCAAATACAGCTTTGGTGCCACCTGCGTGAAGAAGTGTCCCCGTAATTATGTGGTGACAGATCACGGCTCGTGCGTCCGAGCCTGTGGGGCCGACAGCTATGAGATGGAGGAAGACGGCGTCCGCAAGTGTAAGAAGTGCGAAGGGCCTTGCCGCAAAGTGTGTAACGGAATAGGTATTGGTGAATTTAAAGACTCACTCTCCATAAATGCTACGAATATTAAACACTTCAAAAACTGCACCTCCATCAGTGGCGATCTCCACATCCTGCCGGTGGCATTTAGGGGTGACTCCTTCACACATACTCCTCCTCTGGATCCACAGGAACTGGATATTCTGAAAACCGTAAAGGAAATCACAGGGTTTTTGCTGATTCAGGCTTGGCCTGAAAACAGGACGGACCTCCATGCCTTTGAGAACCTAGAAATCATACGCGGCAGGACCAAGCAACATGGTCAGTTTTCTCTTGCAGTCGTCAGCCTGAACATAACATCCTTGGGATTACGCTCCCTCAAGGAGATAAGTGATGGAGATGTGATAATTTCAGGAAACAAAAATTTGTGCTATGCAAATACAATAAACTGGAAAAAACTGTTTGGGACCTCCGGTCAGAAAACCAAAATTATAAGCAACAGAGGTGAAAACAGCTGCAAGGCCACAGGCCAGGTCTGCCATGCCTTGTGCTCCCCCGAGGGCTGCTGGGGCCCGGAGCCCAGGGACTGCGTCTCTTGCCGGAATGTCAGCCGAGGCAGGGAATGCGTGGACAAGTGCAACCTTCTGGAGGGTGAGCCAAGGGAGTTTGTGGAGAACTCTGAGTGCATACAGTGCCACCCAGAGTGCCTGCCTCAGGCCATGAACATCACCTGCACAGGACGGGGACCAGACAACTGTATCCAGTGTGCCCACTACATTGACGGCCCCCACTGCGTCAAGACCTGCCCGGCAGGAGTCATGGGAGAAAACAACACCCTGGTCTGGAAGTACGCAGACGCCGGCCATGTGTGCCACCTGTGCCATCCAAACTGCACCTACGGATGCACTGGGCCAGGTCTTGAAGGCTGTCCAACGAATGGGCCTAAGATCCCGTCCATCGCCACTGGGATGGTGGGGGCCCTCCTCTTGCTGCTGGTGGTGGCCCTGGGGATCGGCCTCTTCATGCGAAGGCGCCACATCGTTCGGAAGCGCACGCTGCGGAGGCTGCTGCAGGAGAGGGAGCTTGTGGAGCCTCTTACACCCAGTGGAGAAGCTCCCAACCAAGCTCTCTTGAGGATCTTGAAGGAAACTGAATTCAAAAAGATCAAAGTGCTGGGCTCCGGCGCGTTCGGCACGGTGTATAAGGGACTCTGGATCCCAGAAGGTGAGAAAGTTAAAATTCCCGTCGCTATCAAGGAATTAAGAGAAGCAACATCTCCGAAAGCCAACAAGGAAATCCTCGATGAAGCCTACGTGATGGCCAGCGTGGACAACCCCCACGTGTGCCGCCTGCTGGGCATCTGCCTCACCTCCACCGTGCAGCTCATCACGCAGCTCATGCCCTTCGGCTGCCTCCTGGACTATGTCCGGGAACACAAAGACAATATTGGCTCCCAGTACCTGCTCAACTGGTGTGTGCAGATCGCAAAGGGCATGAACTACTTGGAGGACCGTCGCTTGGTGCACCGCGACCTGGCAGCCAGGAACGTACTGGTGAAAACACCGCAGCATGTCAAGATCACAGATTTTGGGCTGGCCAAACTGCTGGGTGCGGAAGAGAAAGAATACCATGCAGAAGGAGGCAAAGTGCCTATCAAGTGGATGGCATTGGAATCAATTTTACACAGAATCTATACCCACCAGAGTGATGTCTGGAGCTACGGCGTGACAGTTTGGGAACTAATGACCTTTGGCTCCAAGCCCTATGACGGAATCCCTGCCAGCGAGATCTCCTCCATCCTGGAGAAAGGAGAACGCCTCCCTCAGCCACCCATATGTACCATCGATGTCTACATGATCATGGTCAAGTGCTGGATGATAGACGCAGATAGTCGCCCAAAGTTCCGTGAGTTAATCATCGAATTCTCCAAAATGGCCCGAGACCCCCAGCGCTACCTTGTCATTCAGGGGGATGAAAGAATGCATTTGCCAAGTCCTACAGACTCCAACTTCTACCGTGCCCTGATGGATGAAGAAGACATGGACGACGTTGTGGATGCTGATGAGTACCTNIPCCCTCAGCAGGGCTTCTTCAGCAGCCCCTCCACGTCACGGACTCCCCTCCTGAGCTCTCTGAGTGCAACCAGCAACAATTCCACCGTGGCTTGCATTGATAGAAATGGGCTGCAAAGCTGTCCCATCAAGGAAGACAGCTTCTTGCAGCGATACAGCTCAGACCCCACAGGCGCCTTGACTGAGGACAGCATAGACGACACCTTCCTCCCAGTGCCTGAATACATAAACCAGTCCGTTCCCAAAAGGCCCGCTGGCTCTGTGCAGAATCCTGTCTATCACAATCAGCCTCTGAACCCCGCGCCCAGCAGAGACCCACACTACCAGGACCCCCACAGCACTGCAGTGGGCAACCCCGAGTATCTCAACACTGTCCAGCCCACCTGTGTCAACAGCACATTCGACAGCCCTGCCCACTGGGCCCAGAAAGGCAGCCACCAAATTAGCCTGGACAACCCTGACTACCAGCAGGACTTCTTTCCCAAGGAAGCCAAGCCAAATGGCATCTTTAAGGGCTCCACAGCTGAAAATGCAGAATACCTAAGGGTCGCGCCACAAAGCAGTGAATTTATTGGAGCATGA"
    base_rna = base_dna.replace("T", "U")
    
    sequences = []
    for idx in range(count):
        target = targets[idx % len(targets)]
        seq_type = sequence_types[idx % len(sequence_types)]
        
        # Generate variations by creating mutations or truncations
        if seq_type == "Protein":
            seq_str = base_protein
            # Introduce mutation
            if idx % 3 == 0:
                pos = random.randint(100, len(seq_str) - 100)
                seq_str = seq_str[:pos] + "M" + seq_str[pos+1:]
            name = f"{target} Kinase Domain Protein (Variant {idx+1})"
            desc = f"Homo sapiens {target} receptor tyrosine kinase, simulated isoform {idx+1}"
        elif seq_type == "DNA":
            seq_str = base_dna[:random.randint(400, 800)]
            name = f"{target} DNA Coding Fragment (Clone {idx+1})"
            desc = f"Simulated PCR amplicon for human {target} exon mapping"
        else: # RNA
            seq_str = base_rna[:random.randint(300, 600)]
            name = f"{target} Transcript mRNA Fragment (Isoform {idx+1})"
            desc = f"Simulated messenger RNA fragment for transcriptomics validation"
            
        sequences.append({
            "sequence_id": f"SEQ-{idx+1:05d}",
            "name": name,
            "description": desc,
            "sequence_type": seq_type,
            "sequence_string": seq_str
        })
        
    return sequences

# =====================================================================
# AUDIT CRYPTO TRAIL GENERATOR
# =====================================================================
def get_audit_trail_hash(timestamp_str, action, service_name, user_id, prev_hash):
    payload = f"{timestamp_str}|{action}|{service_name}|{user_id or ''}|{prev_hash or ''}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

# =====================================================================
# SEEDING EXECUTION
# =====================================================================
def seed_all():
    print("Connecting and starting database seed operations...")
    
    # -----------------------------------------------------------------
    # 1. AUTH SERVICE SEEDING
    # -----------------------------------------------------------------
    print("Seeding AUTH service...")
    conn = get_connection("auth")
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE gen_auth.user_roles, gen_auth.role_permissions, gen_auth.users, gen_auth.roles, gen_auth.permissions CASCADE;")
    
    # Insert Roles
    cur.execute("INSERT INTO gen_auth.roles (name, description) VALUES (%s, %s) RETURNING id;", ("Administrator", "System-wide admin access"))
    admin_role_id = cur.fetchone()[0]
    cur.execute("INSERT INTO gen_auth.roles (name, description) VALUES (%s, %s) RETURNING id;", ("Scientist", "Standard research and data capture access"))
    scientist_role_id = cur.fetchone()[0]
    
    # Insert Permissions
    permissions = [
        ("read_metadata", "Read metadata entities"),
        ("write_metadata", "Create and edit metadata"),
        ("read_chemistry", "Query chemical structures"),
        ("write_chemistry", "Register compounds"),
        ("read_bioinformatics", "View sequence datasets"),
        ("run_workflows", "Execute scientific pipelines"),
        ("sign_off_experiments", "Electronically sign experimental results")
    ]
    perm_ids = []
    for name, desc in permissions:
        cur.execute("INSERT INTO gen_auth.permissions (name, description) VALUES (%s, %s) RETURNING id;", (name, desc))
        perm_ids.append(cur.fetchone()[0])
        
    # Link permissions to Administrator (all) and Scientist (read/run/sign)
    for pid in perm_ids:
        cur.execute("INSERT INTO gen_auth.role_permissions (role_id, permission_id) VALUES (%s, %s);", (admin_role_id, pid))
    for pid in perm_ids:
        cur.execute("INSERT INTO gen_auth.role_permissions (role_id, permission_id) VALUES (%s, %s);", (scientist_role_id, pid))
        
    # Insert Users
    hashed_pwd = "$2b$12$6K/z5T.U7i2Fmgp.mB199O1X/qVzE.W4G8oex1XQy3ZtN3t32UreS"
    
    cur.execute("INSERT INTO gen_auth.users (email, hashed_password, full_name, role, is_active) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                ("admin@genquantaa.com", hashed_pwd, "Dr. Sarah Connor", "Administrator", True))
    admin_user_id = cur.fetchone()[0]
    cur.execute("INSERT INTO gen_auth.user_roles (user_id, role_id) VALUES (%s, %s);", (admin_user_id, admin_role_id))
    
    cur.execute("INSERT INTO gen_auth.users (email, hashed_password, full_name, role, is_active) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                ("scientist@genquantaa.com", hashed_pwd, "Dr. John Connor", "Scientist", True))
    scientist_user_id = cur.fetchone()[0]
    cur.execute("INSERT INTO gen_auth.user_roles (user_id, role_id) VALUES (%s, %s);", (scientist_user_id, scientist_role_id))
    
    conn.commit()
    conn.close()
    print("AUTH service seeded successfully.")

    # -----------------------------------------------------------------
    # 2. CHEMINFORMATICS SEEDING (connector.compounds)
    # -----------------------------------------------------------------
    print("Seeding CHEMINFORMATICS service...")
    compounds_pool = generate_compounds(550)
    
    conn = get_connection("chem")
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE connector.compounds CASCADE;")
    
    for idx, cmp in enumerate(compounds_pool):
        # We explicitly supply created_at
        cur.execute(
            "INSERT INTO connector.compounds (entity_key, name, smiles, created_at) VALUES (%s, %s, %s, %s);",
            (cmp["entity_key"], cmp["name"], cmp["smiles"], datetime.utcnow())
        )
    conn.commit()
    conn.close()
    print(f"CHEMINFORMATICS: Seeded {len(compounds_pool)} compounds.")

    # -----------------------------------------------------------------
    # 3. METADATA SERVICE SEEDING (EAV)
    # -----------------------------------------------------------------
    print("Seeding METADATA service (EAV)...")
    conn = get_connection("metadata")
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE metadata.metadata_values, metadata.metadata_entities, metadata.metadata_relationships, metadata.metadata_versions, metadata.metadata_sync_history CASCADE;")
    
    # Check or insert fields
    fields_list = [
        ("target_protein", "Target Protein", "string", "Assay"),
        ("ic50_nm", "IC50 (nM)", "numeric", "Assay"),
        ("ec50_nm", "EC50 (nM)", "numeric", "Assay"),
        ("result_date", "Result Date", "date", "Assay"),
        ("compound_id", "Compound ID", "string", "Assay"),
        ("mw", "Molecular Weight", "numeric", "Chemistry"),
        ("clogp", "cLogP", "numeric", "Chemistry"),
        ("hbd", "H-Bond Donors", "numeric", "Chemistry"),
        ("hba", "H-Bond Acceptors", "numeric", "Chemistry"),
        ("smiles", "SMILES", "string", "Chemistry"),
        ("project", "Project", "string", "Chemistry"),
        ("study_phase", "Study Phase", "string", "Clinical"),
        ("principal_investigator", "PI", "string", "Clinical")
    ]
    
    field_ids = {}
    for name, disp, dtype, cat in fields_list:
        cur.execute("SELECT id FROM metadata.metadata_fields WHERE name = %s;", (name,))
        res = cur.fetchone()
        if res:
            field_ids[name] = res[0]
        else:
            cur.execute(
                "INSERT INTO metadata.metadata_fields (name, display_name, data_type, description, category, is_required) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                (name, disp, dtype, f"Field for {name}", cat, False)
            )
            field_ids[name] = cur.fetchone()[0]
            
    # Seed Compounds into EAV
    print("  Inserting 500+ EAV compound entities...")
    target_proteins = ["EGFR", "HER2", "BRAF V600E", "BCR-ABL", "ALK", "PD-1", "KRAS", "TP53"]
    projects = ["Oncology Target Discovery", "Immunotherapy Screen", "ALK Resistant Mutation Study", "Cardiovascular Safety Screen"]
    
    compound_db_ids = {}
    for cmp in compounds_pool:
        # Create Entity
        cur.execute(
            "INSERT INTO metadata.metadata_entities (entity_key, entity_type, name, description) VALUES (%s, %s, %s, %s) RETURNING id;",
            (cmp["entity_key"], "Compound", cmp["name"], f"Seeded chemical compound analogue: {cmp['name']}")
        )
        entity_id = cur.fetchone()[0]
        compound_db_ids[cmp["entity_key"]] = entity_id
        
        # Calculate/Get properties
        props = calculate_chemical_properties(cmp["smiles"])
        
        # Insert EAV values
        cmp_values = [
            (field_ids["mw"], str(props["mw"])),
            (field_ids["clogp"], str(props["clogp"])),
            (field_ids["hbd"], str(props["hbd"])),
            (field_ids["hba"], str(props["hba"])),
            (field_ids["smiles"], cmp["smiles"]),
            (field_ids["project"], random.choice(projects)),
            (field_ids["target_protein"], random.choice(target_proteins))
        ]
        
        for fid, val in cmp_values:
            cur.execute(
                "INSERT INTO metadata.metadata_values (entity_id, field_id, value) VALUES (%s, %s, %s);",
                (entity_id, fid, val)
            )
            
    # Seed Assays into EAV (1000+ records)
    print("  Inserting 1000+ EAV assay records...")
    assay_targets = [
        ("EGFR Kinase Inhibition", "EGFR"),
        ("HER2 Cell Viability", "HER2"),
        ("BRAF V600E Enzymatic Screen", "BRAF V600E"),
        ("BCR-ABL Profiling", "BCR-ABL"),
        ("ALK Autophosphorylation Assay", "ALK"),
        ("PD-1 Binding Affinity", "PD-1"),
        ("KRAS G12D Binding Screen", "KRAS"),
        ("TP53 Transcriptional Activation", "TP53")
    ]
    
    for idx in range(1050):
        assay_key = f"ASSAY-{idx+1:05d}"
        a_name, target = random.choice(assay_targets)
        comp_key = random.choice(compounds_pool)["entity_key"]
        
        cur.execute(
            "INSERT INTO metadata.metadata_entities (entity_key, entity_type, name, description) VALUES (%s, %s, %s, %s) RETURNING id;",
            (assay_key, "Assay", f"{a_name} - Run {idx+1}", f"High-throughput screening assay data for {target}")
        )
        entity_id = cur.fetchone()[0]
        
        ic50 = round(10 ** random.uniform(-1.0, 4.0), 3) # logarithmic distribution
        ec50 = round(ic50 * random.uniform(1.1, 5.0), 3)
        res_date = (datetime.now() - timedelta(days=random.randint(1, 400))).date().isoformat()
        
        assay_values = [
            (field_ids["target_protein"], target),
            (field_ids["ic50_nm"], str(ic50)),
            (field_ids["ec50_nm"], str(ec50)),
            (field_ids["result_date"], res_date),
            (field_ids["compound_id"], comp_key)
        ]
        
        for fid, val in assay_values:
            cur.execute(
                "INSERT INTO metadata.metadata_values (entity_id, field_id, value) VALUES (%s, %s, %s);",
                (entity_id, fid, val)
            )
            
    conn.commit()
    conn.close()
    print("METADATA (EAV) service seeded successfully.")

    # -----------------------------------------------------------------
    # 4. BIOINFORMATICS SERVICE SEEDING
    # -----------------------------------------------------------------
    print("Seeding BIOINFORMATICS service...")
    conn = get_connection("bio")
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE bio.sequence_annotations, bio.sequence_versions, bio.sequences, bio.alignments, bio.sequence_clusters CASCADE;")
    
    seqs_pool = generate_sequences(110)
    seq_db_ids = []
    
    for s in seqs_pool:
        # Explicitly supply created_at
        cur.execute(
            "INSERT INTO bio.sequences (sequence_id, name, description, sequence_type, sequence_string, created_at) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
            (s["sequence_id"], s["name"], s["description"], s["sequence_type"], s["sequence_string"], datetime.utcnow())
        )
        db_id = cur.fetchone()[0]
        seq_db_ids.append((db_id, s["sequence_id"], s["sequence_type"], s["sequence_string"]))
        
        # Add initial version
        cur.execute(
            "INSERT INTO bio.sequence_versions (sequence_db_id, version, sequence_string, modified_by, change_summary, modified_at) VALUES (%s, %s, %s, %s, %s, %s);",
            (db_id, 1, s["sequence_string"], "system", "Initial sequence import", datetime.utcnow())
        )
        
        # Add annotations
        if s["sequence_type"] == "Protein":
            cur.execute(
                "INSERT INTO bio.sequence_annotations (sequence_id, feature_type, start, \"end\", strand, name, notes) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                (db_id, "domain", 718, 964, 1, "Tyrosine Kinase Domain", "Functional domain containing ATP binding pocket")
            )
            cur.execute(
                "INSERT INTO bio.sequence_annotations (sequence_id, feature_type, start, \"end\", strand, name, notes) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                (db_id, "active_site", 790, 791, 1, "T790", "Gatekeeper residue often mutated to methionine during drug resistance")
            )
        elif s["sequence_type"] == "DNA":
            cur.execute(
                "INSERT INTO bio.sequence_annotations (sequence_id, feature_type, start, \"end\", strand, name, notes) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                (db_id, "exon", 50, 250, 1, "Exon 19 Fragment", "Deletion hot spot in EGFR patient samples")
            )
            cur.execute(
                "INSERT INTO bio.sequence_annotations (sequence_id, feature_type, start, \"end\", strand, name, notes) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                (db_id, "primer_binding", 5, 25, 1, "EGFR-Forward-Primer", "Standard PCR screening primer binding site")
            )
            
    # Seed alignments (explicit created_at)
    print("  Inserting bio alignments...")
    align_data = """CLUSTAL W multiple sequence alignment

SEQ-00001        MRPSGTAGAALLALLAALCPASRALEEKKVCQGTSNKLTQLGTFEDHFLSLQRMFNNCEV
SEQ-00002        MRPSGTAGAALLALLAALCPASRALEEKKVCQGTSNKLTQLGTFEDHFLSLQRMFNNCEV
SEQ-00003        MRPSGTAGAALLALLAALCPASRALEEKKVCQGTSNKLTQLGTFEDHFLSLQRMFNNCEV
consensus        ************************************************************

SEQ-00001        VLGNLEITYVQRNYDLSFLKTIQEVAGYVLIALNTVERIPLENLQIIRGNMYYENSYALA
SEQ-00002        VLGNLEITYVQRNYDLSFLKTIQEVAGYVLIALNTVERIPLENLQIIRGNMYYENSYALA
SEQ-00003        VLGNLEITYVQRNYDLSFLKTIQEVAGYVLIALNTVERIPLENLQIIRGNMYYENSYALA
consensus        ************************************************************"""
    
    cur.execute(
        "INSERT INTO bio.alignments (name, alignment_type, sequences_metadata, alignment_data, score, consensus, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s);",
        ("EGFR Isoform Alignment", "multiple", json.dumps({"seq_ids": ["SEQ-00001", "SEQ-00002", "SEQ-00003"]}), align_data, 100.0, "MRPSGTAGAALLALLAALCPASRALEEKKVCQGTSNKLTQLGTFEDHFLSLQRMFNNCEVVLGNLEITYVQRNYDLSFLKTIQEVAGYVLIALNTVERIPLENLQIIRGNMYYENSYALA", datetime.utcnow())
    )
    
    # Seed clusters (explicit created_at)
    print("  Inserting sequence clustering run...")
    labels = ["SEQ-00001", "SEQ-00002", "SEQ-00003", "SEQ-00004", "SEQ-00005"]
    matrix_values = [
        [0.0, 0.05, 0.12, 0.35, 0.40],
        [0.05, 0.0, 0.09, 0.32, 0.38],
        [0.12, 0.09, 0.0, 0.30, 0.35],
        [0.35, 0.32, 0.30, 0.0, 0.10],
        [0.40, 0.38, 0.35, 0.10, 0.0]
    ]
    matrix_data = {"labels": labels, "values": matrix_values}
    linkage_tree = [[0, 1, 0.05, 2], [3, 4, 0.10, 2], [2, 5, 0.105, 3], [6, 7, 0.33, 5]]
    
    cur.execute(
        "INSERT INTO bio.sequence_clusters (name, method, distance_metric, matrix_json, linkage_json, created_at) VALUES (%s, %s, %s, %s, %s, %s);",
        ("Kinase Family Tree", "UPGMA", "identity", json.dumps(matrix_data), json.dumps(linkage_tree), datetime.utcnow())
    )
    
    conn.commit()
    conn.close()
    print("BIOINFORMATICS service seeded successfully.")

    # -----------------------------------------------------------------
    # 5. WORKFLOW SERVICE SEEDING
    # -----------------------------------------------------------------
    print("Seeding WORKFLOW service...")
    conn = get_connection("workflow")
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE workflow.workflow_approvals, workflow.workflow_steps, workflow.workflow_runs, workflow.workflow_definitions CASCADE;")
    
    # Seed definitions (10 distinct definitions)
    wf_names = [
        ("High-Throughput Assay Data Intake", "Pipeline to parse, validate and upload primary screening assay files to Metadata Catalog"),
        ("SAR Analysis Pipeline", "Identifies R-groups, scaffold alignment, and flags activity cliffs dynamically"),
        ("Lead Optimization Screening", "Filters compounds by ADMET criteria and calculates likeness descriptors"),
        ("Audit Signature Chain Validation", "Checks the cryptographic integrity of FDA-compliant signature logs"),
        ("Protein Structure Docking Workflow", "Models target protein domains and simulates compound binding free energy"),
        ("Next-Gen Sequencing Quality Check", "Aligns read files to target transcripts and generates variant logs"),
        ("Automated LIMS Assay Sync", "Synchronizes local experimental assays with remote database systems"),
        ("AI Scientist Compound Design Helper", "Proposes novel drug analogues utilizing generative LLM services"),
        ("Compound Library Registration", "Validates structure drawings, checks duplicates and updates chemical database"),
        ("Clinical Trial Metadata Processing", "Aggregates clinical endpoints and tracks PI approvals")
    ]
    
    for idx, (w_name, w_desc) in enumerate(wf_names):
        nodes = [
            {"id": "node_1", "type": "input", "data": {"label": "Data Source Input"}},
            {"id": "node_2", "type": "process", "data": {"label": "Validation Step"}},
            {"id": "node_3", "type": "process", "data": {"label": "Analytics Calculation"}},
            {"id": "node_4", "type": "approval", "data": {"label": "Manager E-Signature Sign-off"}},
            {"id": "node_5", "type": "output", "data": {"label": "Publish to Repository"}}
        ]
        edges = [
            {"id": "e1-2", "source": "node_1", "target": "node_2"},
            {"id": "e2-3", "source": "node_2", "target": "node_3"},
            {"id": "e3-4", "source": "node_3", "target": "node_4"},
            {"id": "e4-5", "source": "node_4", "target": "node_5"}
        ]
        
        cur.execute(
            "INSERT INTO workflow.workflow_definitions (name, description, nodes_json, edges_json, trigger_type, is_active, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;",
            (w_name, w_desc, json.dumps(nodes), json.dumps(edges), "MANUAL", True, datetime.utcnow(), datetime.utcnow())
        )
        def_id = cur.fetchone()[0]
        
        # Create 5 runs per definition (50 runs total)
        for r_idx in range(5):
            status = "COMPLETED" if r_idx < 4 else ("FAILED" if r_idx == 4 else "RUNNING")
            cur.execute(
                "INSERT INTO workflow.workflow_runs (workflow_id, status, started_at, finished_at, current_step_idx, logs) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                (def_id, status, datetime.utcnow() - timedelta(hours=6), datetime.utcnow() if status != "RUNNING" else None, 4 if status == "COMPLETED" else 2, f"Starting run {r_idx+1} for workflow {w_name}...\nExecution successfully routed to worker node.")
            )
            run_id = cur.fetchone()[0]
            
            # Create step runs (5 steps per run)
            step_statuses = ["COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED"]
            if status == "FAILED":
                step_statuses = ["COMPLETED", "COMPLETED", "FAILED", "PENDING", "PENDING"]
            elif status == "RUNNING":
                step_statuses = ["COMPLETED", "COMPLETED", "PENDING", "PENDING", "PENDING"]
                
            for s_idx, s_status in enumerate(step_statuses):
                step_id = f"step_{s_idx+1}"
                step_name = nodes[s_idx]["data"]["label"]
                node_type = nodes[s_idx]["type"]
                
                cur.execute(
                    "INSERT INTO workflow.workflow_steps (run_id, step_id, step_name, node_type, status, inputs_json, outputs_json, logs, execution_time_ms) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (run_id, step_id, step_name, node_type, s_status, json.dumps({"param": "value"}), json.dumps({"result": "value"}) if s_status == "COMPLETED" else "{}", f"Executing {step_name}... Done.", 120.5)
                )
                
            # Create approvals (for step 4)
            if status == "COMPLETED" or (status == "RUNNING" and step_statuses[3] == "COMPLETED"):
                cur.execute(
                    "INSERT INTO workflow.workflow_approvals (run_id, step_id, role_required, status, requested_at, completed_at, approved_by, signature_hash, comment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (run_id, "step_4", "Administrator", "APPROVED", datetime.utcnow() - timedelta(hours=1), datetime.utcnow(), "admin@genquantaa.com", "sig_hash_chain_demo_" + str(run_id), "Verified all experimental parameters and compounds align with QA standards.")
                )
                
    conn.commit()
    conn.close()
    print("WORKFLOW service seeded successfully.")

    # -----------------------------------------------------------------
    # 6. COMPLIANCE & AUDIT SERVICE SEEDING
    # -----------------------------------------------------------------
    print("Seeding COMPLIANCE & AUDIT service...")
    conn = get_connection("audit")
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE audit.audit_versions, audit.signature_events, audit.electronic_signatures, audit.entity_versions, audit.audit_logs CASCADE;")
    
    # Seed Electronic Signatures (20 signatures)
    esig_ids = []
    for idx in range(25):
        timestamp = datetime.utcnow() - timedelta(days=idx)
        username = "admin@genquantaa.com" if idx % 2 == 0 else "scientist@genquantaa.com"
        sig_hash = hashlib.sha256(f"{username}|{timestamp.isoformat()}|signature_manifest".encode("utf-8")).hexdigest()
        
        cur.execute(
            "INSERT INTO audit.electronic_signatures (user_id, username, signature_hash, created_at) VALUES (%s, %s, %s, %s) RETURNING id;",
            ("admin_id_1" if idx % 2 == 0 else "scientist_id_2", username, sig_hash, timestamp)
        )
        esig_ids.append(cur.fetchone()[0])
        
    # Seed Signature Events
    for idx, esig_id in enumerate(esig_ids):
        cur.execute(
            "INSERT INTO audit.signature_events (signature_id, action_type, entity_id, reason, meaning, timestamp, details_json) VALUES (%s, %s, %s, %s, %s, %s, %s);",
            (esig_id, "SIGN_OFF_EXPERIMENT", f"RUN-{idx+100}", "Confirming assay results", "I approve this scientific data package", datetime.utcnow(), json.dumps({"verified_columns": ["ic50", "ec50"]}))
        )
        
    # Seed Entity Versions
    entity_ver_ids = []
    for idx in range(40):
        ent_key = f"CMP-{idx+1:05d}"
        sig_hash = hashlib.sha256(f"{ent_key}|version_{idx}".encode("utf-8")).hexdigest()
        cur.execute(
            "INSERT INTO audit.entity_versions (entity_type, entity_id, version, data_json, modified_by, modified_at, change_summary, is_deleted, hash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;",
            ("MetadataEntity", ent_key, 1, json.dumps({"entity_key": ent_key, "entity_type": "Compound", "name": f"Compound {idx+1}"}), "admin@genquantaa.com", datetime.utcnow(), "Initial insert", 0, sig_hash)
        )
        entity_ver_ids.append(cur.fetchone()[0])
        
    # Seed Audit Logs (120 logs with a cryptographically valid SHA-256 hash chain!)
    print("  Generating 120 cryptographically chained audit logs...")
    actions = [
        ("LOGIN_SUCCESS", "auth_service", "/api/v1/auth/login"),
        ("CREATE_METADATA_FIELD", "metadata_service", "/api/v1/metadata/fields"),
        ("CREATE_METADATA_ENTITY", "metadata_service", "/api/v1/metadata/entities"),
        ("EXECUTE_QUERY", "query_service", "/api/v1/query/execute"),
        ("REGISTER_COMPOUND", "cheminformatics_service", "/api/v1/compounds"),
        ("RUN_MSA_ALIGNMENT", "bioinformatics_service", "/api/v1/alignments/multiple"),
        ("CREATE_WORKFLOW", "workflow_service", "/api/v1/workflow/definitions"),
        ("APPROVE_WORKFLOW_STEP", "workflow_service", "/api/v1/workflow/runs/approve"),
        ("GENERATE_INSIGHTS", "ai_service", "/api/v1/ai/chat/query")
    ]
    
    prev_hash = None
    for idx in range(120):
        act, svc, endp = actions[idx % len(actions)]
        timestamp = datetime.utcnow() - timedelta(minutes=(120 - idx) * 15)
        # Use exact string conversion logic for chain verification compatibility
        timestamp_str = timestamp.isoformat()
        user_id = "admin_id_1" if idx % 2 == 0 else "scientist_id_2"
        username = "admin@genquantaa.com" if idx % 2 == 0 else "scientist@genquantaa.com"
        
        # Calculate valid chain hash
        log_hash = get_audit_trail_hash(
            timestamp_str=timestamp_str,
            action=act,
            service_name=svc,
            user_id=user_id,
            prev_hash=prev_hash
        )
        
        details = {"log_index": idx, "description": f"Audited operation {act} for service {svc} completed."}
        
        cur.execute(
            "INSERT INTO audit.audit_logs (timestamp, user_id, username, action, service_name, endpoint, status, ip_address, details_json, previous_hash, hash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;",
            (timestamp, user_id, username, act, svc, endp, "SUCCESS", "127.0.0.1", json.dumps(details), prev_hash, log_hash)
        )
        audit_log_id = cur.fetchone()[0]
        
        # Link some to Entity Versions
        if idx < len(entity_ver_ids):
            cur.execute(
                "INSERT INTO audit.audit_versions (audit_log_id, entity_version_id) VALUES (%s, %s);",
                (audit_log_id, entity_ver_ids[idx])
            )
            
        prev_hash = log_hash
        
    conn.commit()
    conn.close()
    print("COMPLIANCE & AUDIT service seeded successfully.")

    # -----------------------------------------------------------------
    # 7. AI SCIENTIST COPILOT SERVICE SEEDING
    # -----------------------------------------------------------------
    print("Seeding AI Scientist Copilot service...")
    conn = get_connection("ai")
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE ai.chat_messages, ai.chat_sessions CASCADE;")
    
    chat_dialogues = [
        # Session 1: Compound Analogue Screening
        [
            ("user", "Hello Copilot. I need to find potential kinase inhibitor analogues in our local catalog similar to Gefitinib. Can you look up some options?"),
            ("assistant", "Hello! I can certainly assist you with structure exploration. I am scanning the local `cheminformatics` database and joining with the `genquantaa_metadata` EAV catalog to look for structural analogues. Let me compile the Tanimoto similarity metrics.")
        ],
        # Session 2: Bioinformatics Sequence Resistance Mutants
        [
            ("user", "I am analyzing EGFR mutations that might cause drug resistance to Erlotinib or Gefitinib. Do we have any annotated sequences representing this?"),
            ("assistant", "Yes, in our Bioinformatics module, we have registered the Homo sapiens EGFR receptor tyrosine kinase sequence containing the T790M resistance gatekeeper mutation. The T790M mutant has a methionine substitution (M) at position 790 instead of the wild-type threonine (T). This mutation increases ATP affinity, preventing binding of competitive kinase inhibitors.")
        ],
        # Session 3: Workflow Run Audit & Compliance
        [
            ("user", "Can you verify if our latest Lead Optimization Screening workflow run completed successfully and was electronically signed off?"),
            ("assistant", "I am querying the Workflow and Compliance audit databases. Workflow definition 'Lead Optimization Screening' has a completed run (ID 24) on the server. Manager sign-off step was approved and electronically signed by admin@genquantaa.com with cryptographic signature hash chain verification.")
        ],
        # Session 4: SAR Matrix Analysis
        [
            ("user", "Analyze the SAR activity profile of our benzene-based derivatives tested against EGFR. What are the key activity cliffs?"),
            ("assistant", "I have reviewed the SAR decomposition matrix. Introducing a fluorine atom (-F) at position R1 increases EGFR kinase inhibition (IC50 = 4.2 nM) relative to a chlorine atom (-Cl) substituent (IC50 = 125 nM). This indicates a significant 30-fold activity cliff sensitive to electronegative size at the R1 site.")
        ],
        # Session 5: Pipeline Launch assistance
        [
            ("user", "Help me build and launch a High-Throughput Assay Data Intake pipeline in our workflow designer."),
            ("assistant", "I can guide you step-by-step. The workflow template includes: 1. Input Node (LIMS CSV reader), 2. Validation Node (Data clean and parse), 3. Audit Logging, and 4. Electronic Signature Sign-off. Would you like me to generate the node configuration payload?")
        ]
    ]
    
    for s_idx, dialog in enumerate(chat_dialogues):
        cur.execute(
            "INSERT INTO ai.chat_sessions (title, created_at) VALUES (%s, %s) RETURNING id;",
            (f"Scientific Research Inquiry - Topic {s_idx+1}", datetime.utcnow() - timedelta(hours=s_idx))
        )
        sess_id = cur.fetchone()[0]
        
        for m_idx, (role, content) in enumerate(dialog):
            cur.execute(
                "INSERT INTO ai.chat_messages (session_id, role, content, citations_json, created_at) VALUES (%s, %s, %s, %s, %s);",
                (sess_id, role, content, json.dumps([{"source": "local_database", "entity": "CMP-00001"}]) if role == "assistant" else "[]", datetime.utcnow() - timedelta(minutes=(len(dialog) - m_idx) * 10))
            )
            
    conn.commit()
    conn.close()
    print("AI Scientist Copilot service seeded successfully.")

    # -----------------------------------------------------------------
    # 8. QUERY & DASHBOARD TEMPLATE SEEDING
    # -----------------------------------------------------------------
    print("Seeding QUERY & DASHBOARD service templates...")
    conn = get_connection("query")
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE query.analysis_workspaces, query.query_history, query.query_templates CASCADE;")
    
    # Query Templates
    templates = [
        ("EGFR Inhibitors vs Assay Join", "Federated query joining EAV Compounds with EAV Assays on compound_id for EGFR target",
         "{\"name\":\"EGFR Inhibitors Join\",\"nodes\":[{\"id\":\"1\",\"type\":\"compounds\"},{\"id\":\"2\",\"type\":\"assays\"}],\"edges\":[{\"source\":\"1\",\"target\":\"2\",\"joinOn\":\"compound_id\"}]}",
         "SELECT c.entity_key, c.name, c.smiles, a.ic50_nm, a.target_protein FROM metadata.metadata_entities c JOIN metadata.metadata_values v1 ON c.id = v1.entity_id JOIN metadata.metadata_fields f1 ON v1.field_id = f1.id JOIN metadata.metadata_entities a ON a.entity_type = 'Assay' WHERE f1.name = 'target_protein' AND v1.value = 'EGFR'"),
        
        ("High MW Compounds Screening", "Filters chemical libraries for molecules with molecular weight > 500 g/mol",
         "{\"name\":\"High MW Filter\",\"nodes\":[{\"id\":\"1\",\"type\":\"compounds\"}],\"filters\":[{\"field\":\"mw\",\"op\":\">\",\"value\":\"500\"}]}",
         "SELECT entity_key, name, smiles FROM metadata.compounds WHERE mw > 500")
    ]
    
    for t_name, t_desc, t_layout, t_sql in templates:
        cur.execute(
            "INSERT INTO query.query_templates (name, description, layout_json, sql_preview, created_by) VALUES (%s, %s, %s, %s, %s);",
            (t_name, t_desc, t_layout, t_sql, "admin@genquantaa.com")
        )
        
    # Query History
    for idx in range(25):
        cur.execute(
            "INSERT INTO query.query_history (sql, status, execution_time_ms, row_count, error_message, created_at) VALUES (%s, %s, %s, %s, %s, %s);",
            (f"SELECT * FROM compounds WHERE clogp > {round(random.uniform(1.0, 4.0), 1)} LIMIT 10", "SUCCESS", 12.5, 10, None, datetime.utcnow() - timedelta(hours=idx))
        )
        
    # Workspaces
    cur.execute(
        "INSERT INTO query.analysis_workspaces (name, description, query_history_id, dataset_json, configs_json, created_at) VALUES (%s, %s, %s, %s, %s, %s);",
        ("Lead Optimization Workspace", "Dynamic workspace analyzing kinase derivatives binding affinity", 1, "{}", "{}", datetime.utcnow().date().isoformat())
    )
    
    conn.commit()
    conn.close()
    print("QUERY & DASHBOARD service templates seeded successfully.")

    print("\n" + "="*60)
    print(" GENQUANTAA DISCOVER SYSTEM SEEDING COMPLETED SUCCESSFULLY!")
    print(" All microservices loaded with realistic compliance data.")
    print(" Ready for verification checks and presentation dashboards.")
    print("="*60 + "\n")

if __name__ == "__main__":
    seed_all()
