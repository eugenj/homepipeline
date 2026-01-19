# Russian Math School Parent Portal API Documentation

## Authentication System
- **Provider**: Auth0 OAuth2 with PKCE
- **Base Auth URL**: `https://auth.parents.russianschool.com`
- **Main Portal**: `https://parents.mathschool.com/parent-portal/`

## Credentials & Security

### Secure Password Storage Options

1. **AWS Secrets Manager** (recommended for Lambda):
   - Secret Name: `rsm-credentials`
   - Region: `us-east-1`
   - Format: `{"email": "evgeny.zhuravlev@gmail.com", "password": "..."}`

2. **Local Secure File**:
   - Location: `~/.rsm_credentials`
   - Format: `{"email": "evgeny.zhuravlev@gmail.com", "password": "..."}`
   - Permissions: 600 (owner read/write only)

**Setup Instructions

**Local Development:**
```bash
python rsm_setup.py
# Choose option 1 for local only, or 3 for both local and AWS
```

**AWS Lambda:**
```bash
# Option 1: Use rsm_setup.py (recommended)
python rsm_setup.py  # Choose option 2 or 3

# Option 2: Manual AWS CLI (if rsm_setup.py fails)
aws secretsmanager create-secret \
  --name rsm-credentials \
  --description "RSM Parent Portal credentials" \
  --secret-string file://~/.rsm_credentials
```

**Lambda IAM Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:rsm-credentials-*"
    }
  ]
}
```

## Student IDs
- **Student 1**: 163934
- **Student 2**: 183013  
- **Student 3**: 267501

## API Endpoints

### Authentication Flow
1. **Challenge**: `GET https://auth.parents.russianschool.com/usernamepassword/challenge`
2. **Login**: `POST https://auth.parents.russianschool.com/usernamepassword/login`
3. **Token Exchange**: `POST https://auth.parents.russianschool.com/oauth/token`

### GraphQL API
- **Endpoint**: `https://parents.mathschool.com/parent-portal/graphql`
- **Method**: POST
- **Content-Type**: application/json

#### Get Student Enrollments
```graphql
query GetStudentEnrollments($studentId: Long!, $academicEndYear: Int) {
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
}
```

**Variables:**
- `studentId`: 163934 | 183013 | 267501
- `academicEndYear`: 2026

#### Get Student Assignments
```graphql
query GetStudentAssignments($studentId: Long!, $classId: Long!, $types: [SectionTypeEnum]) {
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
}
```

**Variables:**
- `studentId`: Student ID from enrollments
- `classId`: Class ID from enrollments (where state = "ENROLLED")
- `types`: ["HOMEWORK"]

## Authentication Headers Required
```
Accept: application/json, text/plain, */*
Authorization: Bearer {token_from_network_requests}
Content-Type: application/json
Origin: https://parents.mathschool.com
Referer: https://parents.mathschool.com/parent-portal/splash
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
```

## Data Flow
1. **Login via browser automation** to get Bearer token from network requests
2. **Get enrollments** for each student ID to find their class IDs
3. **Get assignments** for each enrolled class ID
4. **Parse results** to extract lesson topics, scores, grades, homework status

## Sample Class IDs Found
- **Student 163934**: Classes 103501, 103514
- **Student 183013**: Classes 103546, 103566
- **Student 267501**: Classes 102348, 103721, 100403

## Assignment Data Structure
- **Lesson Number**: Integer
- **Topic**: String (lesson description)
- **HW Score**: Integer (0-100)
- **Letter Grade**: A_PLUS, A, A_MINUS, B_PLUS, B, B_MINUS, C_PLUS, INC, MISS
- **Homework Status**: HAS_FILE_REVIEWED, NO_FILE_REVIEWED, HAS_UPDATED_FILE_AFTER_REVIEW

## Implementation Script
- **File**: `rsm.py`
- **Function**: Automated login → token extraction → enrollment query → assignment retrieval
- **Output**: Complete academic data for all students and classes
