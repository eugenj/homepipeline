import json
import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Check if spirit.com returns HTTP 200 status
    """
    logger.info(f"Starting spirit.com health check v2...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get('https://spirit.com', timeout=30, headers=headers)
        
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
