import json
import requests
import logging
import boto3
import os
from botocore.exceptions import ClientError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_password():
    """Get password from AWS Secrets Manager"""
    try:
        session = boto3.session.Session()
        client = session.client('secretsmanager', region_name='us-east-1')
        
        secret_response = client.get_secret_value(SecretId='rsm-credentials')
        secret = json.loads(secret_response['SecretString'])
        return secret['password']
        
    except (ClientError, KeyError, json.JSONDecodeError) as e:
        logger.error(f"Failed to get credentials: {e}")
        raise Exception("No password found in AWS Secrets Manager")

def get_bearer_token(email, password):
    """Login and extract Bearer token from network requests"""
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--single-process')
    options.add_argument('--no-zygote')
    options.add_argument('--remote-debugging-port=9222')
    
    # Lambda-specific Chrome configuration
    if os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
        # Running in Lambda - use Chrome layer
        options.binary_location = '/opt/chrome/chrome'
        options.add_argument('--user-data-dir=/tmp/chrome-user-data')
        options.add_argument('--data-path=/tmp/chrome-data')
        options.add_argument('--homedir=/tmp')
        options.add_argument('--disk-cache-dir=/tmp/chrome-cache')
        
        # Try multiple possible ChromeDriver locations
        chromedriver_paths = ['/opt/chromedriver', '/opt/bin/chromedriver', '/usr/local/bin/chromedriver']
        service = None
        
        for path in chromedriver_paths:
            if os.path.exists(path):
                service = Service(path)
                logger.info(f"Using ChromeDriver at: {path}")
                break
        
        if service:
            driver = webdriver.Chrome(service=service, options=options)
        else:
            logger.warning("ChromeDriver not found, trying without service")
            driver = webdriver.Chrome(options=options)
    else:
        # Running locally
        driver = webdriver.Chrome(options=options)
    
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    try:
        driver.get("https://parents.mathschool.com/parent-portal/")
        time.sleep(3)
        
        email_field = driver.find_element(By.CSS_SELECTOR, "input[id*='email']")
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        
        email_field.send_keys(email)
        password_field.send_keys(password)
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # Scroll to button and wait
        driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
        time.sleep(2)
        
        # Try JavaScript click if regular click fails
        try:
            login_button.click()
        except:
            driver.execute_script("arguments[0].click();", login_button)
        time.sleep(5)
        
        driver.get("https://parents.mathschool.com/parent-portal/content/student/267501/academics")
        time.sleep(8)
        
        try:
            logs = driver.get_log('performance')
            
            for log in logs:
                message = json.loads(log['message'])
                if (message['message']['method'] == 'Network.requestWillBeSent' and 
                    'graphql' in message['message']['params']['request']['url']):
                    
                    headers = message['message']['params']['request'].get('headers', {})
                    auth_header = headers.get('Authorization', '')
                    
                    if auth_header.startswith('Bearer '):
                        token = auth_header.replace('Bearer ', '')
                        logger.info("Bearer token retrieved successfully")
                        return token
        except Exception as e:
            logger.error(f"Could not get network logs: {e}")
        
        return None
        
    finally:
        driver.quit()

def get_student_data(session, student_ids):
    """Get academic data for all students"""
    all_data = {}
    
    for student_id in student_ids:
        logger.info(f"Processing student {student_id}")
        
        # Get enrollments
        enrollment_query = {
            "operationName": "GetStudentEnrollments",
            "variables": {
                "studentId": student_id,
                "academicEndYear": 2026
            },
            "query": """query GetStudentEnrollments($studentId: Long!, $academicEndYear: Int) {
              studentEnrollments(studentId: $studentId, academicEndYear: $academicEndYear) {
                id
                registrationId
                dateEnrolled
                dateCancelled
                state
                classId
                transferClassId
                semesterId
                stateChangedOn
                studentId
                __typename
              }
            }"""
        }
        
        response = session.post('https://parents.mathschool.com/parent-portal/graphql', json=enrollment_query)
        
        enrolled_class_ids = []
        if response.status_code == 200:
            data = response.json()
            enrollments = data.get('data', {}).get('studentEnrollments', [])
            enrolled_class_ids = [enrollment['classId'] for enrollment in enrollments if enrollment['state'] == 'ENROLLED']
            logger.info(f"Student {student_id}: {len(enrolled_class_ids)} enrolled classes")
        else:
            logger.error(f"Failed to get enrollments for student {student_id}: {response.status_code}")
            continue
        
        student_data = {}
        
        # Get assignments for each class
        for class_id in enrolled_class_ids:
            query = {
                "operationName": "GetStudentAssignments",
                "variables": {
                    "studentId": student_id,
                    "classId": class_id,
                    "types": ["HOMEWORK"]
                },
                "query": """query GetStudentAssignments($studentId: Long!, $classId: Long!, $types: [SectionTypeEnum]) {
                  assignmentsForStudent(classId: $classId, studentId: $studentId, types: $types) {
                    assignmentItemCount
                    id
                    createdOn
                    context {
                      classId
                      lessonNumber
                      lessonTopic
                      title
                      __typename
                    }
                    letterGrade
                    score
                    bonusScore
                    hwAttachmentsState
                    __typename
                  }
                }"""
            }
            
            response = session.post('https://parents.mathschool.com/parent-portal/graphql', json=query)
            
            if response.status_code == 200:
                data = response.json()
                assignments = data.get('data', {}).get('assignmentsForStudent', [])
                
                if assignments:
                    student_data[f"Class_{class_id}"] = assignments
                    logger.info(f"Student {student_id}, Class {class_id}: {len(assignments)} assignments")
            else:
                logger.error(f"Failed to get assignments for student {student_id}, class {class_id}: {response.status_code}")
        
        all_data[f"Student_{student_id}"] = student_data
    
    return all_data

def lambda_handler(event, context):
    """
    Lambda function to fetch RSM academic data for all students
    """
    
    try:
        email = "evgeny.zhuravlev@gmail.com"
        student_ids = [163934, 183013, 267501]
        
        # Get password from Secrets Manager
        password = get_password()
        
        # Get Bearer token
        logger.info("Getting Bearer token...")
        bearer_token = get_bearer_token(email, password)
        
        if not bearer_token:
            raise Exception("Could not retrieve Bearer token")
        
        # Setup session with token
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json',
            'Origin': 'https://parents.mathschool.com',
            'Referer': 'https://parents.mathschool.com/parent-portal/splash',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Get academic data
        academic_data = get_student_data(session, student_ids)
        
        # Count total assignments
        total_assignments = sum(
            len(assignments) 
            for student_data in academic_data.values() 
            for assignments in student_data.values()
        )
        
        logger.info(f"Successfully retrieved academic data: {len(academic_data)} students, {total_assignments} total assignments")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'RSM academic data retrieved successfully',
                'students_processed': len(academic_data),
                'total_assignments': total_assignments,
                'data': academic_data,
                'timestamp': context.aws_request_id
            })
        }
        
    except Exception as e:
        error_message = f"ERROR: Failed to retrieve RSM data: {str(e)}"
        logger.error(error_message)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': error_message,
                'timestamp': context.aws_request_id
            })
        }
