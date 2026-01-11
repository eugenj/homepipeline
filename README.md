# HomePipeline - Spirit.com Monitor

A serverless application that checks if spirit.com returns HTTP 200 status every hour using AWS Lambda.

## Architecture
- **AWS Lambda**: Python 3.11 function that makes HTTP request to spirit.com
- **EventBridge**: Scheduled rule that triggers Lambda every hour
- **CloudWatch**: Logging and monitoring
- **GitHub Actions**: CI/CD pipeline for automated testing and deployment

## Project Structure
```
homepipeline/
├── lambda_function.py         # Main Lambda handler
├── requirements.txt          # Python dependencies
├── template.yaml            # SAM template for AWS resources
├── tests/
│   └── test_lambda_function.py
├── .github/workflows/
│   └── deploy.yml           # CI/CD pipeline
└── README.md               # This file
```

## Local Development

### Prerequisites
- Python 3.11
- AWS CLI configured
- AWS SAM CLI

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Build SAM application
sam build

# Deploy to AWS
sam deploy --guided
```

## CI/CD Pipeline
The GitHub Actions workflow automatically:
1. Runs tests on every push/PR
2. Deploys to AWS on pushes to main branch (after tests pass)

### Required GitHub Secrets
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY` 
- `AWS_DEFAULT_REGION`

## Monitoring
- CloudWatch logs: `/aws/lambda/homepipeline-checker`
- Function runs every hour via EventBridge schedule
- 7-day log retention policy
