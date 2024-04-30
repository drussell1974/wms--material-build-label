import sys
sys.path.append('../src/')

from unittest import TestCase, skip, main
from unittest.mock import MagicMock, Mock, patch
from mattress_build.app.Mattress_Builds import JobCardDocument, JobCardData

class test_component_JobCardDocument(TestCase):

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
            

    @patch.object(JobCardData, "get_all", return_value=[])
    def test_init_called_build__no_return_rows(self, mock_datasource):
        
        # arrange
        
        # act
        
        self.model = JobCardDocument(source_file="", source_data="")

        self.model.generate_new_label("Sheet1")

        # assert
        self.assertEqual(1, mock_datasource.call_count)

        self.assertEqual(0, len(self.model.pages))


    @patch.object(JobCardData, "get_all", return_value=[])
    def test_init_called_build__return_item(self, mock_datasource):
        
        # arrange

        # act
        self.model = JobCardDocument(source_file="", source_data="")

        self.model.generate_new_label()

        # assert
        self.assertEqual(1, mock_datasource.call_count)

        self.assertEqual(0, len(self.model.pages))


if __name__ == '__main__':
    main()
