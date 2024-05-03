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
        self.source_file = source_file
        self.doc = None
        self.source_data = source_data
        self.build_data = None
        self.pages = []
        self.html = ""

    ''' properties '''

    
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
        return sku_prefix


    def _append_html(self, page, build_data, font_size_pt=10):
        """ append the build information to the page as an html table"""        
        SHRINK_FONT_WHEN_ROWS = 12

        text = ""
        
        if len(build_data) > SHRINK_FONT_WHEN_ROWS:
            # adjust font size for the number of items (TODO: handle divide by zero error)
            font_size_pt * (SHRINK_FONT_WHEN_ROWS / len(build_data))
        
        # build the html table

        for line in build_data:
            text = text + f"<tr><td>{line[0].strip()}</td><td>{line[1]}</td></tr>"
        
        self.html = f"<body><table>{text}</table></body>"

        # set the area for the bill of materials textarea
        rect = page.rect + (5, 250, -5, -5)

        # we must specify an Archive because of the image
        page.insert_htmlbox(rect, self.html, archive=fitz.Archive("."), css="* {font-family: sans-serif;font-size:" + str(font_size_pt) + "pt;}")


    def _get_doc_pages(self):
        return enumerate(self.doc)
    

    ''' public methods '''

    def generate_new_label(self, table_name="Builds", on_jobcardpage_error=None):
        """ process the full_dataset and append the build information to the PDF """
        
        self.doc = fitz.open(self.source_file)
        
        if self.doc is None:
            raise FileNotFoundError(f"Document '{self.source_file}' not opened!")
        
        full_dataset = JobCardDataAccess.get_all(self.source_data, table_name=table_name)

        for page_num, page in self._get_doc_pages():
            sku_prefix = self._extract_sku(page)

            # get the build data for the SKU prefix
            self.build_data = JobCardDataAccess.get_build_data(full_dataset, sku_prefix, on_jobcardpage_error, source_data=self.source_data, page_num=page_num)
            if self.build_data is None or len(self.build_data) == 0:
                self.build_data = [f"No build data found for SKU prefix: '{sku_prefix}'"]
            else:
                # append the build data to the page
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
    QTY_COL_NAME = 'Unnamed: 5'
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
    def get_build_data(cls, full_dataset, sku_prefix, on_jobcarddataaccess_error=None, **kwargs):
        """ get the build information for the SKU prefix
            return: string with semi-colon seperated values of data """
        ''' ref https://pandas.pydata.org/pandas-docs/version/1.3/user_guide/indexing.html#indexing-lookup '''
        
        # initialise return value as None
        build_data = []
        
        try:
            # clean the data and add to a dataframe for lookup
            df_all_rows = pd.DataFrame(full_dataset, columns=[cls.SKU_PREFIX_COL_NAME, cls.SKU_COL_NAME, cls.MATERIALS_COL_NAME, cls.QTY_COL_NAME])
            
            # get row for selected sku_prefix
            df_subset_first_line = df_all_rows[df_all_rows[cls.SKU_PREFIX_COL_NAME].str.contains(sku_prefix, na=False)]
            
            # check if this is the first row containing the value 'Material' in the column
            if len(df_subset_first_line) == 0 or df_subset_first_line.values[0][2] != "Material":
                '''raise error to be caught by the calling function e.g. to be displayed or logged'''
                raise KeyError(f"Row for '{sku_prefix}' does no contain the value 'Material' column.", "row:", df_subset_first_line.values[0], "expected value='Material', actual value='", df_subset_first_line.values[0][2], "'")    
            
            else:
                '''get the build data from rows below the selected line (ensure fillna has been applied to the dataframe)''' 
                df_all_below_first_line = df_all_rows[df_all_rows.index > df_subset_first_line.index[0]]
                # get materials and qty columns
                df_materials_rows = pd.DataFrame(df_all_below_first_line, columns=[cls.MATERIALS_COL_NAME, cls.QTY_COL_NAME])
                # find first empty row
                all_build_data = df_materials_rows.fillna('')
                
                # get the material and qty
                # TODO: value for the selected row then but check the cls.SKU_PREFIX_COL_NAME column is not a sku
                
                # get rows until the first empty row
                for build_item in all_build_data.values:
                    # check if the item is empty 
                    if len(build_item) > 0 and build_item[0].strip(" ").upper() in cls.EMPTY_MATERIAL_VALUES:
                        # final item reached - exit the loop
                        break
                    else:
                        # adding item material and qty to build_data as tuple (two values per item)
                        build_data.append((build_item[0], build_item[1]))
                
        except KeyError as ky_err:
            if on_jobcarddataaccess_error is not None:
                on_jobcarddataaccess_error(ky_err, **kwargs)
            else:
                raise ky_err
        except IndexError as idx_err:
            if on_jobcarddataaccess_error is not None:
                on_jobcarddataaccess_error(idx_err, **kwargs)
            else:
                raise idx_err
            
        return build_data


# program entry point

# error handling

def handle_general_error(e):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(f"* FATAL ERROR...")
    print(f"* An error occurred: {e} ")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


def handle_jobcardpage_error(e, source_data=None, page_num=0):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(f" Error: {e}.\n\nPAGE {page_num} MAY NOT CONTAIN BUILD DATA.")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(" 1. Check labels before applying to product. ")
    print(f" 2. Check {source_data}. ")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


if __name__ == '__main__':

    try:
        # settings

        source_file = './tests/data/Original job card TEST.pdf'
        full_dataset_file = './tests/data/Build Materials Data TEST.xlsx'
        output_file = './tests/data/Build Materials job card TEST.pdf'
        
        # open the job card template

        doc = JobCardDocument(source_file, full_dataset_file)

        doc.generate_new_label("Builds", on_jobcardpage_error=handle_jobcardpage_error)
        
        doc.save_and_close(output_file)

        print("**************************************************************")
        print("* Modified PDF with adjusted text properties has been saved. *")
        print("**************************************************************")
    
    except Exception as e:
        handle_general_error(e)
        raise e
    
