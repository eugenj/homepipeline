import json
import requests
import logging
import boto3
import os
import re
import urllib.parse
from botocore.exceptions import ClientError

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

def get_bearer_token_headless(email, password):
    """Login using requests and extract Bearer token"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    try:
        # Step 1: Get the initial login page
        logger.info("Getting initial login page...")
        response = session.get('https://parents.mathschool.com/parent-portal/')
        
        if response.status_code != 200:
            raise Exception(f"Failed to load portal: {response.status_code}")
        
        # Extract Auth0 login URL from redirects or page content
        auth_url = None
        if 'auth.parents.russianschool.com' in response.url:
            auth_url = response.url
        else:
            # Look for Auth0 URL in page content
            auth_match = re.search(r'https://auth\.parents\.russianschool\.com/[^"\']+', response.text)
            if auth_match:
                auth_url = auth_match.group(0)
        
        if not auth_url:
            raise Exception("Could not find Auth0 login URL")
        
        logger.info(f"Found Auth0 URL: {auth_url[:50]}...")
        
        # Step 2: Get the Auth0 login form
        response = session.get(auth_url)
        if response.status_code != 200:
            raise Exception(f"Failed to load Auth0 page: {response.status_code}")
        
        # Step 3: Extract form data and CSRF token
        csrf_match = re.search(r'name="_csrf"\s+value="([^"]+)"', response.text)
        state_match = re.search(r'name="state"\s+value="([^"]+)"', response.text)
        
        if not csrf_match or not state_match:
            raise Exception("Could not find CSRF token or state in login form")
        
        csrf_token = csrf_match.group(1)
        state = state_match.group(1)
        
        logger.info("Extracted form tokens")
        
        # Step 4: Submit login credentials
        login_data = {
            'state': state,
            'username': email,
            'password': password,
            'action': 'default',
            '_csrf': csrf_token
        }
        
        login_url = 'https://auth.parents.russianschool.com/usernamepassword/login'
        response = session.post(login_url, data=login_data, allow_redirects=True)
        
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.status_code}")
        
        # Step 5: Check if we're back at the portal (successful login)
        if 'parents.mathschool.com' not in response.url:
            raise Exception("Login did not redirect to portal - check credentials")
        
        logger.info("Login successful, making GraphQL request to get token...")
        
        # Step 6: Make a GraphQL request to trigger token usage
        test_query = {
            "operationName": "GetUserSettings",
            "variables": {"userId": 242479994},
            "query": "query GetUserSettings($userId: Int!) { userSettings(userId: $userId) { id } }"
        }
        
        # Try to make GraphQL request and capture the Authorization header
        # This is tricky without browser dev tools, so let's try a different approach
        
        # Step 7: Look for token in cookies or local storage simulation
        # Check if any cookies contain JWT-like tokens
        for cookie in session.cookies:
            if cookie.value and cookie.value.startswith('eyJ'):  # JWT format
                logger.info("Found JWT token in cookies")
                return cookie.value
        
        # If no token found, we need to simulate the SPA token exchange
        # This is complex without browser automation
        raise Exception("Could not extract Bearer token - may need browser automation")
        
    except Exception as e:
        logger.error(f"Headless login failed: {e}")
        raise

def get_student_data(session, student_ids):
    """Get academic data for all students using existing session"""
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
                id classId state __typename
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
                    id score letterGrade hwAttachmentsState
                    context { lessonNumber lessonTopic __typename }
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
    Lambda function to fetch RSM academic data without browser automation
    """
    
    try:
        email = "evgeny.zhuravlev@gmail.com"
        student_ids = [163934, 183013, 267501]
        
        # Get password from Secrets Manager
        password = get_password()
        
        # Try headless login first
        logger.info("Attempting headless login...")
        
        try:
            bearer_token = get_bearer_token_headless(email, password)
            
            # Setup session with token
            session = requests.Session()
            session.headers.update({
                'Accept': 'application/json, text/plain, */*',
                'Authorization': f'Bearer {bearer_token}',
                'Content-Type': 'application/json',
                'Origin': 'https://parents.mathschool.com',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
        except Exception as e:
            logger.warning(f"Headless login failed: {e}")
            # Fallback: return error for now, could implement browser automation as backup
            raise Exception(f"Authentication failed: {e}")
        
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
                'message': 'RSM academic data retrieved successfully (headless)',
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
