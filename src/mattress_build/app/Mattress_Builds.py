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

    def __init__(self, source_file, source_data):
        self.doc = fitz.open(source_file)
        self.source_data = source_data


    def generate_new_label(self, table_name="Builds"):
        # read the build data from the excel file

        build_data = JobCardData.get_all(self.source_data, table_name=table_name)

        for page_num, page in enumerate(self.doc):
            sku_prefix = self._extract_sku(page)

            if sku_prefix and build_data['SKU'].str.contains(sku_prefix).any():
                build_info = build_data[build_data['SKU'].str.startswith(sku_prefix)]['Build'].iloc[0]
                    
            self._append_html(build_info, page)


    def _extract_sku(self, page):

        text = page.get_text("text")
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'SKU Code:' in line and i+1 < len(lines):
                sku = lines[i+1].strip()
                return sku.split('-')[0] if '-' in sku else sku
        return None


    def _append_html(self, build_info, page):
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


    def save_and_close(self, output_file):
        self.doc.save(output_file)
        self.doc.close()


class JobCardData:

    def __init__(self):
        pass

    @staticmethod
    def get_all(source, table_name='Builds'):
        """ get all build data from the excel source file """

        build_data = pd.read_excel(source, sheet_name=table_name)
        build_data['SKU'] = build_data['SKU'].fillna('')

        return build_data


# program entry point

if __name__ == '__main__':

    try:
        # settings

        source_file = './content/drive/My Drive/Aspire/Aspire Production/Mattress Builds/Example job card.pdf'
        build_data_file = './content/drive/My Drive/Aspire/Aspire Production/Mattress Builds/Build Example.xlsx'
        output_file = './content/drive/My Drive/Aspire/Aspire Production/Mattress Builds/Modified Example job card.pdf'

        # open the job card template

        doc = JobCardDocument(source_file, build_data_file)

        doc.generate_new_label(table_name="Sheet1")
        
        doc.save_and_close(output_file)

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