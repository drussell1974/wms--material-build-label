""" Materials Build Labelling """
'''
Read the build data from an Excel file and apply it to the PDF job card.
'''
''' PyMuPDF docs: https://pymupdf.readthedocs.io/en/latest/recipes-text.html '''

import fitz  # PyMuPDF
import os
import pandas as pd
from reportlab.lib.colors import black
from reportlab.pdfgen import canvas
import io

def create_html_snippet(build_info):
    html = """
    <body>
        <table>
        """
    for line in build_info.split(';'):
        html += f"<tr><td>{line.strip()}</td></tr>"
    html += """
        </table>
    </body>
    """
    return html


def extract_sku(text):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if 'SKU Code:' in line and i+1 < len(lines):
            sku = lines[i+1].strip()
            return sku.split('-')[0] if '-' in sku else sku
    return None


build_data = pd.read_excel('./content/drive/My Drive/Aspire/Aspire Production/Mattress Builds/Build Example.xlsx')
build_data['SKU'] = build_data['SKU'].fillna('')

doc = fitz.open('./content/drive/My Drive/Aspire/Aspire Production/Mattress Builds/Example job card.pdf')

for page_num, page in enumerate(doc):
    text = page.get_text("text")
    sku_prefix = extract_sku(text)
    if sku_prefix and build_data['SKU'].str.contains(sku_prefix).any():
        build_info = build_data[build_data['SKU'].str.startswith(sku_prefix)]['Build'].iloc[0]
        
    rect = page.rect + (5, 250, -5, -5)

    text = text + create_html_snippet(build_info)

    # we must specify an Archive because of the image
    page.insert_htmlbox(rect, text, archive=fitz.Archive("."), css="* {font-family: sans-serif;font-size:8px;}")

if not os.path.exists('./content/drive/My Drive/Aspire/Aspire Production/Mattress Builds/Modified Example job card.pdf'):
    doc.ez_save(__file__.replace(".py", ".pdf"))

output_pdf_path = './content/drive/My Drive/Aspire/Aspire Production/Mattress Builds/Modified Example job card.pdf'

doc.save(output_pdf_path)
doc.close()
print("Modified PDF with adjusted text properties has been saved.")
