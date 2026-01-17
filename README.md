# HomePipeline - Spirit.com Monitor

A serverless application that checks if spirit.com returns HTTP 200 status every hour using AWS Lambda.

## Architecture
- **AWS Lambda**: Python 3.11 function that makes HTTP request to spirit.com
- **EventBridge**: Scheduled rule that triggers Lambda every hour
- **CloudWatch**: Logging and monitoring (7-day retention)
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
├── infrastructure-plan.md   # Detailed implementation plan
└── README.md               # This file
```

## Deployment Status
✅ **COMPLETED**: All core functionality is working
- Lambda function deployed and tested
- EventBridge hourly schedule configured
- CloudWatch logging with 7-day retention
- CI/CD pipeline configured (GitHub Actions with OIDC)

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
sam deploy --stack-name homepipeline-stack --capabilities CAPABILITY_IAM --region us-east-1
```

## CI/CD Pipeline
The GitHub Actions workflow automatically:
1. Runs tests on every push/PR
2. Deploys to AWS on pushes to main branch (after tests pass)

### Required GitHub OIDC Setup
- AWS IAM Identity Provider configured for GitHub OIDC
- IAM Role: `GitHubActionsHomePipelineRole` with permissions:
  - AWSCloudFormationFullAccess
  - AWSLambda_FullAccess  
  - IAMFullAccess
  - AmazonS3FullAccess
  - CloudWatchLogsFullAccess
  - AmazonEventBridgeFullAccess

## Monitoring
- **CloudWatch logs**: `/aws/lambda/homepipeline-checker`
- **Function execution**: Every hour via EventBridge schedule
- **Log retention**: 7 days
- **Expected behavior**: Function may return 403 from spirit.com (normal due to bot protection)

## Important Notes
⚠️ **Avoid Manual Deployment After CI/CD Setup**
- Always deploy through GitHub Actions pipeline
- Manual `sam deploy` creates resource conflicts with CI/CD
- If conflicts occur, delete CloudFormation stacks before CI/CD deployment

## Troubleshooting
- **Resource conflicts**: Delete existing `homepipeline-stack` before CI/CD deployment
- **403 responses**: Expected behavior from spirit.com due to bot protection
- **GitHub Actions**: Check workflow logs for deployment status
