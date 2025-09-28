import fitz  # PyMuPDF
import os
def add_watermark(file_path, watermark_text):
    doc = fitz.open(file_path)
    for page in doc:
        rect = fitz.Rect(50, 50, 300, 100)
        page.insert_textbox(rect, watermark_text, fontsize=12, rotate=90, color=(0,0,0), overlay=True)
    doc.save("uploads" + os.path.basename(file_path).replace(".", "_watermarked."))

add_watermark("uploads/sem1_marksheet.pdf", "Sample Watermark")