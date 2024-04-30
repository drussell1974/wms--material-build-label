""" Materials Build Labelling """
"""
 * Copyright (C) 2024 Aspire Furniture <dave.russell@aspire-furniture.co.uk>
 * 
 * This file is part of wms--material-build-label.
 * 
 * wms--material-build-label can not be copied and/or distributed without the express
 * permission of Aspire Furniture
 *******************************************************/
"""
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


class JobCardDocument:

    def __init__(self):
        pass

    @staticmethod
    def get_job_card_template(source):
        """ open the job card template """

        return fitz.open(source)


    def extract_sku(self):

        text = page.get_text("text")
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'SKU Code:' in line and i+1 < len(lines):
                sku = lines[i+1].strip()
                return sku.split('-')[0] if '-' in sku else sku
        return None


    @staticmethod
    def append_build(build_info, page):
        """ append the build information to the page as an html table"""

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
        
        # set the area for the bill of materials textarea

        rect = page.rect + (5, 250, -5, -5)

        # we must specify an Archive because of the image
        page.insert_htmlbox(rect, html, archive=fitz.Archive("."), css="* {font-family: sans-serif;font-size:8px;}")


class MaterialBuild:

    def __init__(self):
        pass

    @staticmethod
    def get_all(source, sheet_name='Builds'):
        """ get all build data from the excel source file """

        build_data = pd.read_excel(source, sheet_name=sheet_name)
        build_data['SKU'] = build_data['SKU'].fillna('')

        return build_data

# run the script

if __name__ == '__main__':

    try:
        # settings

        template_file = './content/drive/My Drive/Aspire/Aspire Production/Mattress Builds/Example job card.pdf'
        build_data_file = './content/drive/My Drive/Aspire/Aspire Production/Mattress Builds/Build Example.xlsx'
        output_file = './content/drive/My Drive/Aspire/Aspire Production/Mattress Builds/Modified Example job card.pdf'

        # read the build data from the excel file

        build_data = MaterialBuild.get_all(build_data_file, sheet_name='Sheet1')

        # open the job card template

        doc = JobCardDocument.get_job_card_template(template_file)

        for page_num, page in enumerate(doc):
            
            sku_prefix = JobCardDocument.extract_sku(page)

            if sku_prefix and build_data['SKU'].str.contains(sku_prefix).any():
                build_info = build_data[build_data['SKU'].str.startswith(sku_prefix)]['Build'].iloc[0]
                
            JobCardDocument.append_build(build_info, page)

        doc.save(output_file)
        doc.close()

        print("**************************************************************")
        print("* Modified PDF with adjusted text properties has been saved. *")
        print("**************************************************************")
    except Exception as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"* FATAL ERROR...")
        print(f"* An error occurred: {e} ")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        raise e