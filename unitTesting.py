import unittest
from unittest.mock import patch
from options_historical_prices import *

class TestGetOptionsTickers(unittest.TestCase):
    @patch('requests.get')
    def test_get_options_tickers(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.json.return_value = {
            'status': 'OK',
            'results': [{'ticker': 'AAPL210917C00145000'}]
        }

        result = get_options_tickers()
        self.assertEqual(result[0], 'AAPL210917C00145000')

class TestGetHistoricalPrices(unittest.TestCase):
    @patch('requests.get')
    def test_get_historical_prices(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.json.return_value = {
            'status': 'OK',
            'results': [{
                'c': 150.0,
                'h': 155.0,
                'l': 145.0,
                'n': 100,
                'o': 150.0,
                't': 1633027200000,
                'v': 10000,
                'vw': 150.0
            }]
        }

        result = get_historical_prices('AAPL210917C00145000')
        expected_result = pd.DataFrame([{
            'Close': 150.0,
            'High': 155.0,
            'Low': 145.0,
            'Number of Transactions': 100,
            'Open': 150.0,
            'Timestamp': pd.to_datetime(1633027200000, unit='ms'),
            'Volume': 10000,
            'Volume Weighted Average Price': 150.0
        }])
        pd.testing.assert_frame_equal(result, expected_result)

if __name__ == '__main__':
    unittest.main()