import pypdf
import os

pdf_path = r"c:\Users\saiki\GENQUANTAA DISCOVER\backend\discovery pplatfoem.pdf"
reader = pypdf.PdfReader(pdf_path)

print("PDF Metadata:")
print(reader.metadata)

print("\nPages analysis:")
for idx, page in enumerate(reader.pages):
    print(f"Page {idx+1}:")
    print(f"  Images count: {len(page.images)}")
    text = page.extract_text()
    print(f"  Text length: {len(text) if text else 0}")
