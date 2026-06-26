import fitz  # PyMuPDF
import os

pdf_path = r"c:\Users\saiki\GENQUANTAA DISCOVER\backend\discovery pplatfoem.pdf"
output_dir = r"c:\Users\saiki\GENQUANTAA DISCOVER\frontend\public\manual_pages"

os.makedirs(output_dir, exist_ok=True)

print(f"Opening PDF: {pdf_path}")
doc = fitz.open(pdf_path)
print(f"Total pages to render: {len(doc)}")

for i in range(len(doc)):
    print(f"Rendering page {i+1}...")
    page = doc[i]
    pix = page.get_pixmap(dpi=150)  # Render at 150 DPI for good readability and file size
    pix.save(os.path.join(output_dir, f"page_{i+1}.png"))

print("All pages rendered and saved successfully!")
