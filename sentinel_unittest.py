import unittest
from unittest.mock import Mock
import geopandas as gpd
import sentinel2overlap as s2o






class TestScript(unittest.TestCase):
    test_data = gpd.read_file('test/sentinel_test.geojson')
    shape = gpd.read_file('Charkiv.geojson')
    overlaps = gpd.read_file('test/overlaps_test.geojson')
    correct_result = ['36UXA', '36UXU', '36UXV', '36UYA', '36UYB', '36UYU', '36UYV', '37UCP', '37UCQ', '37UCR', '37UDQ', '37UDR']

    
    def test_loadSentinel_API(self):
        file_id = '184xXr4eq41SdBDiOOogMy2ajSjKFNT7H'
        service = Mock()
        file = service.files().get(fileId=file_id).execute()     # Gets a file metadata from Google drive, by file ID
        # file['title'] == 'sentinel2tiles.geojson'
        # file['webContentLink'] == "https://drive.google.com/uc?id=184xXr4eq41SdBDiOOogMy2ajSjKFNT7H&export=download" 
        # Get a link from that, plug into gpd.read_file()
        service.files.assert_called()
        self.assertIsNotNone(file)

    def test_loadSentinelReturnsCorrect(self):
        result = s2o.load_sentinel('184xXr4eq41SdBDiOOogMy2ajSjKFNT7H', self.shape)
        self.assertIsInstance(result, gpd.GeoDataFrame)
        

    def test_OverlapReturnsCorrect(self):
        result = s2o.make_overlap_map(self.test_data)
        self.assertIsInstance(result, gpd.geoseries.GeoSeries)

    def test_DropRedundantReturnsCorrect(self):
        result = s2o.drop_redundant(self.test_data, self.shape, self.overlaps)
        self.assertIsInstance(result, list)

    def test_DropRedundantOutputCorrect(self):
        result = s2o.drop_redundant(self.test_data, self.shape, self.overlaps)
        self.assertEqual(result,self.correct_result)

    def test_PrintReturnsNone(self):
        self.assertIsNone(s2o.print_tile_list(self.correct_result))
    
    def test_ReadFilepathsReturnsTuple(self):
        result = s2o.read_filepaths()
        self.assertIsInstance(result, tuple)

if __name__ == '__main__':
    unittest.main()