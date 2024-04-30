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
import pandas as pd


class JobCardDocument:

    def __init__(self, source_file, source_data):

        self.doc = fitz.open(source_file)
        self.source_data = source_data
        self.build_info = None
        self.pages = []
        self.html = ""


    ''' private methods '''

    def _extract_sku(self, page):
        """ extract the SKU from the page """
        
        text = page.get_text("text")
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'SKU Code:' in line and i+1 < len(lines):
                sku = lines[i+1].strip()
                return sku.split('-')[0] if '-' in sku else sku
        return None


    def _append_html(self, page, build_info):
        """ append the build information to the page as an html table"""
        
        text = ""
        for line in build_info:
            text = text + f"<tr><td>{line.strip()}</td></tr>"
        self.html = f"<body><table>{text}</table></body>"

        # set the area for the bill of materials textarea

        rect = page.rect + (5, 250, -5, -5)

        # we must specify an Archive because of the image
        page.insert_htmlbox(rect, self.html, archive=fitz.Archive("."), css="* {font-family: sans-serif;font-size:8px;}")


    def _get_doc_pages(self):
        return enumerate(self.doc)


    ''' public methods '''

    def generate_new_label(self, table_name="Builds"):
        """ process the build_data and append the build information to the PDF """

        build_data = JobCardData.get_all(self.source_data, table_name=table_name)

        for page_num, page in self._get_doc_pages():
            sku_prefix = self._extract_sku(page)
            
            self.build_info = JobCardData.get_build_info(build_data, sku_prefix)
            
            self._append_html(page, self.build_info)

            self.pages.append(page)


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

        print(build_data['SKU'])
        print(type(build_data['SKU']))

        return build_data
    

    @staticmethod
    def get_build_info(build_data, sku_prefix):
        """ get the build information for the SKU prefix """
        build_cols = None
        
        if sku_prefix and build_data['SKU'].str.contains(sku_prefix).any():
            sku = build_data['SKU'].str.startswith(sku_prefix)
            sku_build_data = build_data[sku]
            #print("get sku_build_data['Build']...", sku_build_data)
            build_cols = sku_build_data['Build']
            #print("get - (build_cols:", build_cols, ", type:", type(build_cols), ")...")
            build_cols = build_cols.iloc[0]
        print("build_cols", build_cols)
        print(type(build_cols))

        return build_cols


# program entry point

if __name__ == '__main__':

    try:
        # settings

        source_file = './tests/data/Example job card.pdf'
        build_data_file = './tests/data/Build Example v1.xlsx'
        output_file = './tests/data/Modified Example job card.pdf'

        # open the job card template

        doc = JobCardDocument(source_file, build_data_file)

        doc.generate_new_label("Sheet1")
        
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