try:
    import rdkit
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors
    print("Python RDKit package is installed successfully!")
    mol = Chem.MolFromSmiles("CCO")
    print(f"Can parse SMILES CCO: {mol is not None}")
except Exception as e:
    print(f"Failed to import/use Python RDKit: {e}")
