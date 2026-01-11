import json
import pytest
from unittest.mock import patch, Mock
import sys
import os

# Add parent directory to path to import lambda_function
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import():
    """Test that we can import the lambda function"""
    try:
        import lambda_function
        assert hasattr(lambda_function, 'lambda_handler')
    except ImportError as e:
        pytest.fail(f"Failed to import lambda_function: {e}")

@patch('requests.get')
def test_spirit_com_returns_200(mock_get):
    """Test successful response from spirit.com"""
    # Import here to avoid issues
    from lambda_function import lambda_handler
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    result = lambda_handler({}, {})
    
    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert body['message'] == 'spirit.com is accessible'
    assert body['status_code'] == 200
    mock_get.assert_called_once_with('https://spirit.com', timeout=30)

@patch('requests.get')
def test_spirit_com_returns_non_200(mock_get):
    """Test non-200 response from spirit.com"""
    from lambda_function import lambda_handler
    
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    result = lambda_handler({}, {})
    
    assert result['statusCode'] == 500
    body = json.loads(result['body'])
    assert 'spirit.com returned 404' in body['message']
    assert body['status_code'] == 404

@patch('requests.get')
def test_spirit_com_request_exception(mock_get):
    """Test exception during request to spirit.com"""
    from lambda_function import lambda_handler
    
    mock_get.side_effect = Exception("Connection timeout")
    
    result = lambda_handler({}, {})
    
    assert result['statusCode'] == 500
    body = json.loads(result['body'])
    assert 'Error checking spirit.com: Connection timeout' in body['message']
