import json
import pytest
from unittest.mock import patch, Mock
import sys
import os

# Add parent directory to path to import bbc_monitoring
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import():
    """Test that we can import the bbc_monitoring module"""
    try:
        import bbc_monitoring
        assert hasattr(bbc_monitoring, 'lambda_handler')
    except ImportError as e:
        pytest.fail(f"Failed to import bbc_monitoring: {e}")

@patch('requests.get')
def test_bbc_com_returns_200(mock_get):
    """Test successful response from bbc.com"""
    from bbc_monitoring import lambda_handler
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    result = lambda_handler({}, {})
    
    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert body['message'] == 'bbc.com is accessible'
    assert body['status_code'] == 200
    expected_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    mock_get.assert_called_once_with('https://bbc.com', timeout=30, headers=expected_headers)

@patch('requests.get')
def test_bbc_com_returns_non_200(mock_get):
    """Test non-200 response from bbc.com"""
    from bbc_monitoring import lambda_handler
    
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    result = lambda_handler({}, {})
    
    assert result['statusCode'] == 500
    body = json.loads(result['body'])
    assert 'bbc.com returned 404' in body['message']
    assert body['status_code'] == 404

@patch('requests.get')
def test_bbc_com_request_exception(mock_get):
    """Test exception during request to bbc.com"""
    from bbc_monitoring import lambda_handler
    
    mock_get.side_effect = Exception("Connection timeout")
    
    result = lambda_handler({}, {})
    
    assert result['statusCode'] == 500
    body = json.loads(result['body'])
    assert 'Error checking bbc.com: Connection timeout' in body['message']
