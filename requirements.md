# HomePipeline Project Requirements

## Project Goal
Create an application which performs basic tasks on a regular basis and required infrastructure to develop and deploy the application.

## Application Requirements

### 1. Web Polling Service
- Poll a specified website every 1 hour
- Process HTML content to extract information
- Site URL to be specified later

### 2. Notification System
- Implement rules-based matching on extracted data
- Send notifications when rules are triggered:
  - Email notifications
  - Page notifications (e.g., PagerDuty integration)

## Infrastructure Requirements

### 3. Technology Stack
**Priority: Use free technologies wherever possible**

#### 3.1 Proposed Free Technologies
- **Code Repository**: GitHub (free tier)
- **Runtime Environment**: AWS Lambda (free tier: 1M requests/month)
- **Additional considerations**: 
  - AWS CloudWatch Events/EventBridge for scheduling
  - AWS SES for email notifications
  - GitHub Actions for CI/CD pipeline

#### 3.2 CI/CD Pipeline
- Automated testing pipeline
- Deploy new application versions only if tests pass
- Integration with GitHub for source control
- Automated deployment to AWS Lambda

## Next Steps
- [ ] Define target website and data extraction requirements
- [ ] Set up GitHub repository
- [ ] Configure AWS Lambda environment
- [ ] Implement basic polling application
- [ ] Set up notification rules and integrations
- [ ] Create CI/CD pipeline with GitHub Actions
