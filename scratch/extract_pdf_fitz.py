import fitz  # PyMuPDF
import os

pdf_path = r"c:\Users\saiki\GENQUANTAA DISCOVER\backend\discovery pplatfoem.pdf"
output_path = r"c:\Users\saiki\GENQUANTAA DISCOVER\scratch\discovery_platform_text_fitz.txt"

print(f"Reading PDF with PyMuPDF from: {pdf_path}")
if not os.path.exists(pdf_path):
    print("PDF path does not exist!")
    exit(1)

doc = fitz.open(pdf_path)
print(f"Total pages: {len(doc)}")

text_content = []
for i in range(len(doc)):
    page = doc[i]
    print(f"Processing page {i+1}...")
    text_content.append(f"--- PAGE {i+1} ---")
    text_content.append(page.get_text() or "")

os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(text_content))

print(f"Finished extracting. Text saved to: {output_path}")
