import json
import pytest
from unittest.mock import patch, Mock
import sys
import os

# Add parent directory to path to import rsm_monitoring
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import():
    """Test that we can import the rsm_monitoring module"""
    try:
        import rsm_monitoring
        assert hasattr(rsm_monitoring, 'lambda_handler')
        assert hasattr(rsm_monitoring, 'get_password')
        assert hasattr(rsm_monitoring, 'get_bearer_token')
        assert hasattr(rsm_monitoring, 'get_student_data')
    except ImportError as e:
        pytest.fail(f"Failed to import rsm_monitoring: {e}")

@patch('rsm_monitoring.get_password')
@patch('rsm_monitoring.get_bearer_token')
@patch('rsm_monitoring.get_student_data')
def test_lambda_handler_success(mock_get_student_data, mock_get_bearer_token, mock_get_password):
    """Test successful RSM data retrieval"""
    from rsm_monitoring import lambda_handler
    
    # Mock the dependencies
    mock_get_password.return_value = "test_password"
    mock_get_bearer_token.return_value = "test_bearer_token"
    mock_get_student_data.return_value = {
        "Student_163934": {"Class_103501": [{"id": 1, "score": 100}]},
        "Student_183013": {"Class_103546": [{"id": 2, "score": 95}]},
        "Student_267501": {"Class_102348": [{"id": 3, "score": 98}]}
    }
    
    # Mock context
    context = Mock()
    context.aws_request_id = "test-request-id"
    
    result = lambda_handler({}, context)
    
    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert body['message'] == 'RSM academic data retrieved successfully'
    assert body['students_processed'] == 3
    assert body['total_assignments'] == 3
    assert 'data' in body

@patch('rsm_monitoring.get_password')
def test_lambda_handler_password_failure(mock_get_password):
    """Test failure when password cannot be retrieved"""
    from rsm_monitoring import lambda_handler
    
    mock_get_password.side_effect = Exception("No password found in AWS Secrets Manager")
    
    # Mock context
    context = Mock()
    context.aws_request_id = "test-request-id"
    
    result = lambda_handler({}, context)
    
    assert result['statusCode'] == 500
    body = json.loads(result['body'])
    assert 'No password found in AWS Secrets Manager' in body['error']

@patch('rsm_monitoring.get_password')
@patch('rsm_monitoring.get_bearer_token')
def test_lambda_handler_token_failure(mock_get_bearer_token, mock_get_password):
    """Test failure when bearer token cannot be retrieved"""
    from rsm_monitoring import lambda_handler
    
    mock_get_password.return_value = "test_password"
    mock_get_bearer_token.return_value = None
    
    # Mock context
    context = Mock()
    context.aws_request_id = "test-request-id"
    
    result = lambda_handler({}, context)
    
    assert result['statusCode'] == 500
    body = json.loads(result['body'])
    assert 'Could not retrieve Bearer token' in body['error']
