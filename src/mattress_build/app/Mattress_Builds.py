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
    """ class to handle the job card document """
    
    def __init__(self, source_file, source_data):

        self.doc = fitz.open(source_file)
        self.source_data = source_data
        self.build_data = None
        self.pages = []
        self.html = ""


    ''' private methods '''

    def _extract_sku(self, page):
        """ extract the SKU from the page """
        sku_prefix = None
        text = page.get_text("text")
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'SKU Code:' in line and i+1 < len(lines):
                sku = lines[i+1].strip()
                sku_prefix = sku.split('-')[0] if '-' in sku else sku
        print("def _extract_sku(...) - sku_prefix:", sku_prefix)
        return sku_prefix


    def _append_html(self, page, build_data):
        """ append the build information to the page as an html table"""
        
        text = ""
        for line in build_data.all() if build_data is None else []:
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
        """ process the full_dataset and append the build information to the PDF """

        full_dataset = JobCardDataAccess.get_all(self.source_data, table_name=table_name)

        for page_num, page in self._get_doc_pages():
            sku_prefix = self._extract_sku(page)
            
            self.build_data = JobCardDataAccess.get_build_data(full_dataset, sku_prefix)
            
            if self.build_data is not None:
                self._append_html(page, self.build_data)
                self.pages.append(page)


    def save_and_close(self, output_file):
        self.doc.save(output_file)
        self.doc.close()


class JobCardDataAccess:
    """ class to handle the fetching and processing of the job card data """

    SKU_PREFIX_COL_NAME = 'Pick'
    SKU_COL_NAME = 'Sku'
    MATERIALS_COL_NAME = 'Unnamed: 4'
    QTY_COL_NAME = 'Qty'
    # NOTE: values to be treated as empty (Upper case for case insensitivity)
    EMPTY_MATERIAL_VALUES = ["", "X", "MATERIAL"]

    @staticmethod
    def cleanse(data, column):
        """ cleanse the data by filling NaN values with empty strings """
        
        data[column] = data[column].fillna('')
        return data
        

    @classmethod
    def get_all(cls, source, table_name='Builds'):
        """ get all build data from the excel source file """

        sku_data = cls.cleanse(pd.read_excel(source, sheet_name=table_name), cls.SKU_COL_NAME)        
        return sku_data

    
    @classmethod
    def get_build_data(cls, full_dataset, sku_prefix):
        """ get the build information for the SKU prefix
            return: string with semi-colon seperated values of data """
        ''' ref https://pandas.pydata.org/pandas-docs/version/1.3/user_guide/indexing.html#indexing-lookup '''
        
        # initialise return value as None
        arr_build_data = []
        
        # clean the data and add to a dataframe for lookup
        df_all_rows = pd.DataFrame(full_dataset, columns=[cls.SKU_PREFIX_COL_NAME, cls.SKU_COL_NAME, cls.MATERIALS_COL_NAME, cls.QTY_COL_NAME])
        
        # get row for selected sku_prefix
        df_subset_first_line = df_all_rows[df_all_rows[cls.SKU_PREFIX_COL_NAME].str.contains(sku_prefix, na=False)]
        
        # check if this is the first row containing the value 'Material' in the column
        if df_subset_first_line.values[0][2] != "Material":
            '''raise error to be caught by the calling function e.g. to be displayed or logged'''
            raise KeyError("The line does no contain the value 'Material' column.", "row:", df_subset_first_line.values[0], "expected value='Material', actual value='", df_subset_first_line.values[0][2], "'")    
        
        else:
            '''get the build data from rows below the selected line (ensure fillna has been applied to the dataframe)''' 
            df_all_below_first_line = df_all_rows[df_all_rows.index > df_subset_first_line.index[0]]
            # get materials and qty columns
            df_materials_rows = pd.DataFrame(df_all_below_first_line, columns=[cls.MATERIALS_COL_NAME, cls.QTY_COL_NAME])
            # find first empty row
            df_materials_rows = df_materials_rows.fillna('')
            
            # get the material value for the selected row then but check the cls.SKU_PREFIX_COL_NAME column is not a sku
            all_build_data = df_materials_rows[cls.MATERIALS_COL_NAME] #.str.cat(sep=';')
            # get rows until the first empty row
            for build_item in all_build_data:
                # check if the item is empty 
                if build_item.strip(" ").upper() in cls.EMPTY_MATERIAL_VALUES:
                    # exit the loop
                    break
                else:
                    print("adding item to build_data:", build_item)
                    arr_build_data.append(build_item)
        
        # combine each item seperated with a semi-colon
        return ";".join(arr_build_data)


# program entry point

if __name__ == '__main__':

    try:
        # settings

        source_file = './tests/data/Example job card.pdf'
        full_dataset_file = './tests/data/Build Example v2.xlsx'
        output_file = './tests/data/Modified Example job card.pdf'

        # open the job card template

        doc = JobCardDocument(source_file, full_dataset_file)

        doc.generate_new_label("Builds")
        
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