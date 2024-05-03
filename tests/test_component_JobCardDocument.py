import sys
sys.path.append('../src/')

import pandas as pd

from unittest import TestCase, skip, main
from unittest.mock import MagicMock, Mock, patch
from mattress_build.app.Mattress_Builds import JobCardDocument, JobCardDataAccess

class test_component_JobCardDocument(TestCase):
    
    # MUST BE <class 'pandas.core.frame.DataFrame'> and <class 'pandas.core.series.Series'>
    s1 = pd.Series(["", ""])
    s2 = pd.Series(["0   AA8  Quilted Panel - Cool Touch Diamond (Tac & Jump...", "1   AB8  Test Info 1 ; Test Info 2; Test Info 3; Test I..."])
    
    ## {'col1': [1, 2], 'col2': [3, 4]}
    
    data = {
        'SKU':["0   AA8  Quilted Panel - Cool Touch Diamond (Tac & Jump...","1   AB8  Test Info 1 ; Test Info 2; Test Info 3; Test I..."],
        'Build':[s1, s2]
    }

    # 1-d array of strings
    """fake_full_dataset = pd.DataFrame(data, columns=['SKU','Build'])
    fake_bill_of_materials = [
        'Quilted Panel - Cool Touch Diamond (Tac & Jump Box)',
        '8mm Memory Foam; Superfirm Polyester 400g',
        'Titan Pad',
        'Bonnell Spring Unit',
        'Titan Pad',
        'Superfirm Polyester 400g','Cut Panel - Grey Needle Punch',
        '7.5" Border - Diamond - Plain White Damask'
    ]"""
    
    # 2-d array of strings (material) and integers (qty)
    fake_full_dataset = pd.DataFrame(data, columns=['SKU','Build'])
    fake_bill_of_materials = [
        ('Quilted Panel - Cool Touch Diamond (Tac & Jump Box)', 999),
        ('8mm Memory Foam; Superfirm Polyester 400g', 1),
        ('Titan Pad',3),
        ('Bonnell Spring Unit', 999),
        ('Titan Pad', 0),
        ('Superfirm Polyester 400g','Cut Panel - Grey Needle Punch', 1000),
        ('7.5" Border - Diamond - Plain White Damask', 64)
    ]
        
    def setUp(self):        
        pass 


    def tearDown(self):
        pass


    @patch.object(JobCardDataAccess, "get_all", side_effect=Exception)
    def test_generate_new_label__raises_exception(self, mock_datasource):
        
        # arrange        
        self.model = JobCardDocument(source_file="", source_data="")

        with self.assertRaises(Exception):
            # act
            self.model.generate_new_label()

        # assert
        self.assertEqual(1, mock_datasource.call_count)
        self.assertIsNone(self.model.build_data)
        self.assertEqual(0, len(self.model.pages))
        self.assertEqual("", self.model.html)
        

    @patch.object(JobCardDataAccess, "get_all", return_value=[])
    def test_generate_new_label__datasource_returns_no_rows(self, mock_datasource):
        
        # arrange
        
        with patch.object(JobCardDocument, "_get_doc_pages", return_value=enumerate([])):
            # act
            self.model = JobCardDocument(source_file="", source_data="")

            self.model.generate_new_label()

            # assert
            self.assertEqual(1, mock_datasource.call_count)
            self.assertEqual(1, JobCardDocument._get_doc_pages.call_count)

            self.assertIsNone(self.model.build_data)
            self.assertEqual(0, len(self.model.pages))
            self.assertEqual("", self.model.html)


    @patch.object(JobCardDataAccess, "get_all", return_value=fake_full_dataset)
    @patch.object(JobCardDataAccess, "get_build_data", return_value=fake_bill_of_materials)
    def test_generate_new_label__datasource_returns_multiple_items(self, mock_sku_data, mock_datasource):
        
        # arrange
        fake_text = 'Loreem ipsum'
    
        mock_page = MagicMock()
        mock_page.get_text = MagicMock(return_value=fake_text)
        
        with patch.object(JobCardDocument, "_get_doc_pages", return_value=enumerate((mock_page, mock_page))):
            
            # act
            
            self.model = JobCardDocument(source_file="", source_data="")

            self.model.generate_new_label()

            # assert
            self.assertEqual(1, mock_datasource.call_count)
            self.assertEqual(2, mock_sku_data.call_count)

            self.maxDiff = None
            self.assertEqual(7, len(self.model.build_data))
            self.assertEqual(2, len(self.model.pages))
            self.assertEqual(('Quilted Panel - Cool Touch Diamond (Tac & Jump Box)', 999), self.model.build_data[0], "Should be first item 'Quilted Panel - Cool Touch Diamond (Tac & Jump Box)'")
            self.assertEqual(('7.5" Border - Diamond - Plain White Damask', 64), self.model.build_data[6], "Should be last item ' Cut Panel - Grey Needle Punch'")
            self.assertEqual(2, len(self.model.pages))
            self.assertEqual('<body><table><tr><td>Quilted Panel - Cool Touch Diamond (Tac & Jump Box)</td><td>999</td></tr><tr><td>8mm Memory Foam; Superfirm Polyester 400g</td><td>1</td></tr><tr><td>Titan Pad</td><td>3</td></tr><tr><td>Bonnell Spring Unit</td><td>999</td></tr><tr><td>Titan Pad</td><td>0</td></tr><tr><td>Superfirm Polyester 400g</td><td>Cut Panel - Grey Needle Punch</td></tr><tr><td>7.5" Border - Diamond - Plain White Damask</td><td>64</td></tr></table></body>', self.model.html)

    
    def test_generate_new_label__datasource_raises_error(self):
        # TODO: implement test for when datasource raises an error
        pass


if __name__ == '__main__':
    main()
