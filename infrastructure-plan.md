# HomePipeline Infrastructure Plan - Spirit.com Monitor

## Application Overview
Python-based placeholder application that checks spirit.com returns HTTP 200 response every hour using AWS Lambda.

## Detailed Implementation Steps

### 1. Local Development Setup
**Step 1** - Initialize project structure *(Assignee: Kiro)*
- Create basic Python Lambda function
- Add requirements.txt with requests library
- Create SAM template.yaml for AWS resources

**Step 2** - Implement spirit.com checker *(Assignee: Kiro)*
- Write lambda_function.py with HTTP GET to spirit.com
- Check for 200 status code
- Add basic logging and error handling

**Step 3** - Create unit tests *(Assignee: Kiro)*
- Write test_lambda_function.py
- Mock HTTP responses for testing
- Add pytest configuration

### 2. GitHub Repository Setup
**Step 4** - Create GitHub repository *(Assignee: Human)*
- Go to github.com and create new repository "homepipeline"
- Set repository to public (for free GitHub Actions)
- Initialize with README

**Step 5** - Push local code to GitHub *(Assignee: Kiro)*
- Initialize git in local project
- Add remote origin to GitHub repository
- Push initial code with commit message

### 3. AWS Infrastructure Setup
**Step 6** - Configure AWS credentials *(Assignee: Human)*
- Ensure AWS CLI is configured with valid credentials
- Verify access to Lambda, EventBridge, and CloudWatch services

**Step 7** - Create SAM deployment *(Assignee: Kiro)*
- Build SAM application locally
- Deploy to AWS using `sam deploy --guided`
- Configure stack name as "homepipeline-stack"

**Step 8** - Set up EventBridge schedule *(Assignee: Kiro)*
- Add EventBridge rule to SAM template
- Configure cron expression for hourly execution
- Link rule to Lambda function

### 4. CI/CD Pipeline Creation
**Step 9** - Create GitHub Actions workflow *(Assignee: Kiro)*
- Create .github/workflows/deploy.yml
- Configure Python 3.11 environment
- Add steps for testing and SAM deployment

**Step 10** - Configure GitHub Secrets *(Assignee: Human)*
- Add AWS_ACCESS_KEY_ID to GitHub repository secrets
- Add AWS_SECRET_ACCESS_KEY to GitHub repository secrets
- Add AWS_DEFAULT_REGION (e.g., us-east-1)

**Step 11** - Test CI/CD pipeline *(Assignee: Kiro)*
- Make small code change and push to main branch
- Verify GitHub Actions runs successfully
- Confirm Lambda function updates in AWS

### 5. Monitoring Setup
**Step 12** - Configure CloudWatch monitoring *(Assignee: Kiro)*
- Add CloudWatch alarm for Lambda errors
- Set up log retention policy (7 days)
- Create basic dashboard for function metrics

**Step 13** - Test end-to-end functionality *(Assignee: Human)*
- Manually trigger Lambda function in AWS console
- Verify spirit.com check works correctly
- Check CloudWatch logs for proper execution

### 6. Documentation and Cleanup
**Step 14** - Update project documentation *(Assignee: Kiro)*
- Update README.md with setup instructions
- Document environment variables and configuration
- Add troubleshooting section

**Step 15** - Final validation *(Assignee: Human)*
- Wait for scheduled execution (next hour)
- Verify automatic execution works
- Confirm monitoring alerts are functional

## Project Structure
```
homepipeline/
├── lambda_function.py         # Main Lambda handler
├── requirements.txt          # Python dependencies (requests)
├── template.yaml            # SAM template for AWS resources
├── tests/
│   └── test_lambda_function.py
├── .github/workflows/
│   └── deploy.yml           # CI/CD pipeline
└── README.md               # Project documentation
```

## AWS Resources Created
- **Lambda Function**: homepipeline-checker
- **EventBridge Rule**: hourly-spirit-check
- **IAM Role**: Lambda execution role
- **CloudWatch Log Group**: /aws/lambda/homepipeline-checker

## Key Configuration
- **Target URL**: https://spirit.com
- **Schedule**: Every hour (rate(1 hour))
- **Timeout**: 30 seconds
- **Memory**: 128MB
- **Runtime**: Python 3.11
