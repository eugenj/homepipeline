import json
import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Check if spirit.com returns HTTP 200 status
    """
    logger.info(f"Starting spirit.com health check...")
    try:
        response = requests.get('https://spirit.com', timeout=30)
        
        if response.status_code == 200:
            logger.info(f"SUCCESS: spirit.com returned {response.status_code}")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'spirit.com is accessible',
                    'status_code': response.status_code,
                    'timestamp': context.aws_request_id if context else 'local'
                })
            }
        else:
            logger.warning(f"WARNING: spirit.com returned {response.status_code}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': f'spirit.com returned {response.status_code}',
                    'status_code': response.status_code
                })
            }
            
    except Exception as e:
        logger.error(f"ERROR checking spirit.com: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error checking spirit.com: {str(e)}'
            })
        }
