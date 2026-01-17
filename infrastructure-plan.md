# HomePipeline Infrastructure Plan - Spirit.com Monitor

## Application Overview
Python-based placeholder application that checks spirit.com returns HTTP 200 response every hour using AWS Lambda.

## Detailed Implementation Steps

### 1. Local Development Setup ✅ COMPLETED
**Step 1** - Initialize project structure *(Assignee: Kiro)* ✅
- Create basic Python Lambda function
- Add requirements.txt with requests library
- Create SAM template.yaml for AWS resources

**Step 2** - Implement spirit.com checker *(Assignee: Kiro)* ✅
- Write lambda_function.py with HTTP GET to spirit.com
- Check for 200 status code
- Add basic logging and error handling

**Step 3** - Create unit tests *(Assignee: Kiro)* ✅
- Write test_lambda_function.py
- Mock HTTP responses for testing
- Add pytest configuration

### 2. GitHub Repository Setup ✅ COMPLETED
**Step 4** - Create GitHub repository *(Assignee: Human)* ✅
- Go to github.com and create new repository "homepipeline"
- Set repository to public (for free GitHub Actions)
- Initialize with README

**Step 5** - Push local code to GitHub *(Assignee: Kiro)* ✅
- Initialize git in local project
- Add remote origin to GitHub repository
- Push initial code with commit message

### 3. AWS Infrastructure Setup ✅ COMPLETED
**Step 6** - Configure AWS credentials *(Assignee: Human)* ✅
- Ensure AWS CLI is configured with valid credentials
- Verify access to Lambda, EventBridge, and CloudWatch services


**Step 8** - Set up EventBridge schedule *(Assignee: Kiro)* ✅
- Add EventBridge rule to SAM template
- Configure cron expression for hourly execution
- Link rule to Lambda function
- **NOTE**: Created via SAM template, not manually

### 4. CI/CD Pipeline Creation ✅ COMPLETED
**Step 9** - Create GitHub Actions workflow *(Assignee: Kiro)* ✅
- Create .github/workflows/deploy.yml
- Configure Python 3.11 environment
- Add steps for testing and SAM deployment

**Step 10** - Configure GitHub OIDC Authentication *(Assignee: Human)* ✅
- Create OpenID Connect identity provider in AWS IAM
- Create IAM role: GitHubActionsHomePipelineRole with required permissions:
  - AWSCloudFormationFullAccess
  - AWSLambda_FullAccess  
  - IAMFullAccess
  - AmazonS3FullAccess
  - CloudWatchLogsFullAccess
  - AmazonEventBridgeFullAccess
- Updated workflow to use role-based authentication

**Step 11** - Test CI/CD pipeline *(Assignee: Kiro)* ✅ COMPLETED
- Updated GitHub Actions workflow with OIDC
- Resolved test failures (missing dependencies)
- Resolved authentication issues (OIDC setup)
- Resolved permission issues (CloudFormation access)
- **RESOLVED**: Deleted conflicting CloudFormation stack `homepipeline-stack`
- Environment is now clean for CI/CD deployment

### 5. Monitoring Setup ⏳ IN PROGRESS
**Step 12** - Configure CloudWatch monitoring *(Assignee: Kiro)*
- Add CloudWatch alarm for Lambda errors
- Set up log retention policy (7 days)
- Create basic dashboard for function metrics

**Step 13** - Test end-to-end functionality *(Assignee: Human)*
- Manually trigger Lambda function in AWS console
- Verify spirit.com check works correctly
- Check CloudWatch logs for proper execution

### 6. Documentation and Cleanup ⏳ PENDING
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

## Key Lessons Learned

### ⚠️ IMPORTANT: Avoid Manual Deployment
- **DO NOT** run `sam deploy` manually after setting up CI/CD pipeline
- Manual deployments create resource conflicts with CloudFormation stacks
- Always deploy through GitHub Actions pipeline to maintain consistency

### Resource Conflict Resolution
If manual deployment was done accidentally:
1. Delete conflicting CloudFormation stacks: `aws cloudformation delete-stack --stack-name <stack-name>`
2. Delete individual resources if needed: Lambda functions, EventBridge rules
3. Ensure clean environment before CI/CD deployment

### Required IAM Permissions for GitHub Actions Role
- AWSCloudFormationFullAccess (critical for SAM deployment)
- AWSLambda_FullAccess
- IAMFullAccess  
- AmazonS3FullAccess
- CloudWatchLogsFullAccess
- AmazonEventBridgeFullAccess
