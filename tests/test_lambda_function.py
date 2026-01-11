import json
import pytest
from unittest.mock import patch, Mock
import sys
import os

# Add parent directory to path to import lambda_function
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_function import lambda_handler

class TestLambdaFunction:
    
    @patch('lambda_function.requests.get')
    def test_spirit_com_returns_200(self, mock_get):
        """Test successful response from spirit.com"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = lambda_handler({}, {})
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'spirit.com is accessible'
        assert body['status_code'] == 200
        mock_get.assert_called_once_with('https://spirit.com', timeout=30)
    
    @patch('lambda_function.requests.get')
    def test_spirit_com_returns_non_200(self, mock_get):
        """Test non-200 response from spirit.com"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = lambda_handler({}, {})
        
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'spirit.com returned 404' in body['message']
        assert body['status_code'] == 404
    
    @patch('lambda_function.requests.get')
    def test_spirit_com_request_exception(self, mock_get):
        """Test exception during request to spirit.com"""
        mock_get.side_effect = Exception("Connection timeout")
        
        result = lambda_handler({}, {})
        
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'Error checking spirit.com: Connection timeout' in body['message']
