import sys
sys.path.append('../src/')

import pandas as pd

from unittest import TestCase, skip, main
from unittest.mock import MagicMock, Mock, patch
from mattress_build.app.Mattress_Builds import JobCardDocument, JobCardData

class test_component_JobCardDocument(TestCase):
    
    # MUST BE <class 'pandas.core.frame.DataFrame'> and <class 'pandas.core.series.Series'>
    s1 = pd.Series(["", ""])
    s2 = pd.Series(["0   AA8  Quilted Panel - Cool Touch Diamond (Tac & Jump...", "1   AB8  Test Info 1 ; Test Info 2; Test Info 3; Test I..."])
    
    ## {'col1': [1, 2], 'col2': [3, 4]}
    
    data = {
        'SKU':["0   AA8  Quilted Panel - Cool Touch Diamond (Tac & Jump...","1   AB8  Test Info 1 ; Test Info 2; Test Info 3; Test I..."],
        'Build':[s1, s2]
    }

    fake_build_data = pd.DataFrame(data, columns=['SKU','Build'])
    fake_build_cols = ['Quilted Panel - Cool Touch Diamond (Tac & Jump Box)','8mm Memory Foam; Superfirm Polyester 400g','Titan Pad','Bonnell Spring Unit','Titan Pad','Superfirm Polyester 400g','Cut Panel - Grey Needle Punch','7.5" Border - Diamond - Plain White Damask']
    
    
    def setUp(self):        
        pass 


    def tearDown(self):
        pass


    @patch.object(JobCardData, "get_all", side_effect=Exception)
    def test_init_called_publish__with_exception(self, mock_datasource):
        
        # arrange        
        self.model = JobCardDocument(source_file="", source_data="")

        with self.assertRaises(Exception):
            # act
            self.model.generate_new_label("Sheet1")

        # assert
        self.assertEqual(1, mock_datasource.call_count)
        self.assertIsNone(self.model.build_info)
        self.assertEqual(0, len(self.model.pages))
        self.assertEqual("", self.model.html)
        

    @patch.object(JobCardData, "get_all", return_value=[])
    def test_init_called_build__datasource_return_no_rows(self, mock_datasource):
        
        # arrange
        
        with patch.object(JobCardDocument, "_get_doc_pages", return_value=enumerate([])):
            # act
            self.model = JobCardDocument(source_file="", source_data="")

            self.model.generate_new_label("Sheet1")

            # assert
            self.assertEqual(1, mock_datasource.call_count)
            self.assertEqual(1, JobCardDocument._get_doc_pages.call_count)

            self.assertIsNone(self.model.build_info)
            self.assertEqual(0, len(self.model.pages))
            self.assertEqual("", self.model.html)


    @patch.object(JobCardData, "get_all", return_value=fake_build_data)
    @patch.object(JobCardData, "get_build_info", return_value=fake_build_cols)
    def test_init_called_build__datasource_return_multiple_items(self, mock_sku_data, mock_datasource):
        
        # arrange
        fake_text = '227163\n02/04/24\nDue Date:\nOrder:\n8" Rolled Matt - Aspire Cool Diamond Tile\nQuilted - Double Comfort Non Memory Core\n- White Aspire Cool Diamond Border - 4ft6\n8B-AC-FF-WB-46\nSKU Code:\nAA8-46\nPO 02.04\nPowered by TCPDF (www.tcpdf.org)'

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
            self.assertEqual('Quilted Panel - Cool Touch Diamond (Tac & Jump Box)', self.model.build_info[0], "Should be first item 'Quilted Panel - Cool Touch Diamond (Tac & Jump Box)'")
            self.assertEqual('7.5" Border - Diamond - Plain White Damask', self.model.build_info[7], "Should be last item ' Cut Panel - Grey Needle Punch'")
            self.assertEqual(2, len(self.model.pages))
            #self.assertEqual("<body><table><tr><td></td></tr><tr><td>Quilted Panel - Cool Touch Diamond (Tac & Jump Box)</td></tr><tr><td> Cut Panel - Grey Needle Punch</td></tr></table></body>", self.model.html)


if __name__ == '__main__':
    main()
