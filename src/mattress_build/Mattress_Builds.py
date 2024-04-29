import fitz  # PyMuPDF
import pandas as pd
from reportlab.lib.colors import black
from reportlab.pdfgen import canvas
import io
def create_info_snippet(build_info, x, y):
    packet = io.BytesIO()
    can = canvas.Canvas(packet)
    text = can.beginText(x, y)
    text.setFont("Helvetica-Bold", 38)  # Set font size to 38
    text.setFillColor(black)
    for line in build_info.split(';'):
        text.textLine(line.strip())
    can.drawText(text)
    can.save()
    packet.seek(0)
    return fitz.open("pdf", packet.read())
def extract_sku(text):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if 'SKU Code:' in line and i+1 < len(lines):
            sku = lines[i+1].strip()
            return sku.split('-')[0] if '-' in sku else sku
    return None
build_data = pd.read_excel('/content/drive/My Drive/Aspire/Aspire Production/Mattress Builds/Build Example.xlsx')
build_data['SKU'] = build_data['SKU'].fillna('')
doc = fitz.open('/content/drive/My Drive/Aspire/Aspire Production/Mattress Builds/Example job card.pdf')
for page_num, page in enumerate(doc):
    text = page.get_text("text")
    sku_prefix = extract_sku(text)
    if sku_prefix and build_data['SKU'].str.contains(sku_prefix).any():
        build_info = build_data[build_data['SKU'].str.startswith(sku_prefix)]['Build'].iloc[0]
        info_pdf = create_info_snippet(build_info, -5, 500)  # Start higher up on the page
        # Enlarge the rectangle to accommodate the width of the text
        rect = fitz.Rect(-5, 270, 278, 432)  # Adjusted to be wider
        page.show_pdf_page(rect, info_pdf, pno=0)
output_pdf_path = '/content/drive/My Drive/Aspire/Aspire Production/Mattress Builds/Modified Example job card.pdf'
doc.save(output_pdf_path)
doc.close()
print("Modified PDF with adjusted text properties has been saved.")