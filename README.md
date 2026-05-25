# Automated Employee Onboarding System

**Live Project | AWS Serverless | Event-Driven Architecture**

---

## 1. Problem Statement

HR teams at small and mid-sized companies lose 5–10 hours per new hire manually sending welcome emails, notifying IT, and alerting managers. Errors and delays damage the new employee experience and slow down productivity from day one.

---

## 2. Cloud Solution

A fully automated, event-driven onboarding pipeline built on AWS. When HR submits a new hire record via REST API, the system automatically:
- Sends a personalized welcome email to the new employee
- Sends an IT provisioning alert
- Notifies the manager via SNS
- Logs and tracks the onboarding status in DynamoDB

Zero manual steps. Zero delays.

---

## 3. Architecture

    HR submits new hire (API Gateway POST /onboard)
            ↓
    Lambda #1 — OnboardingIntake
    - Validates payload
    - Writes record to DynamoDB (status: PENDING)
    - Publishes event to EventBridge
            ↓
    EventBridge Rule — NewHireSubmittedRule
    - Listens for source: onboarding.system
            ↓
    Lambda #2 — OnboardingNotify
    - SES → Welcome email to new hire
    - SES → IT provisioning alert
    - SNS → Manager notification
    - Updates DynamoDB status to NOTIFIED
            ↓
    DynamoDB — OnboardingTable
    - Tracks all records, status, timestamps

---

## 4. AWS Services Used

| Service | Role |
|---|---|
| API Gateway | REST API entry point for HR to submit new hires |
| Lambda #1 | Validates input, writes to DynamoDB, fires EventBridge event |
| EventBridge | Decouples intake from notifications (event-driven) |
| Lambda #2 | Sends emails via SES, notification via SNS, updates DynamoDB |
| SES | Sends welcome email and IT provisioning alert |
| SNS | Sends manager notification |
| DynamoDB | Stores all onboarding records and tracks status |
| IAM | Least-privilege roles for each Lambda function |

---

## 5. Key Concepts Demonstrated

- **Event-driven architecture** — services communicate via events, not direct calls
- **Decoupled design** — EventBridge allows adding more targets without modifying Lambda #1
- **Serverless** — no servers to manage, scales automatically
- **Least privilege IAM** — each Lambda has only the permissions it needs
- **Status tracking** — DynamoDB records move from PENDING to NOTIFIED
- **CORS enabled** — API Gateway configured for browser-based access

---

## 6. Business Value

- Eliminates 5–10 hours of manual HR work per new hire
- Ensures consistent onboarding experience for every employee
- Scales automatically — handles 1 or 1,000 new hires with no infrastructure changes
- Fully auditable — every onboarding event is logged in DynamoDB with timestamps
- Extensible — new notifications (Slack, Jira, Active Directory) can be added via EventBridge without touching existing code

---

## 7. DynamoDB Schema

| Attribute | Type | Description |
|---|---|---|
| employeeId | String (PK) | Auto-generated UUID |
| name | String | Full name of new hire |
| email | String | New hire email |
| department | String | Department |
| startDate | String | Start date |
| managerEmail | String | Manager email |
| status | String | PENDING → NOTIFIED |
| createdAt | String | ISO timestamp |
| notifiedAt | String | ISO timestamp of notification |

---

## 8. Deployment Guide

### Prerequisites
- AWS Account
- SES production access (or verified sandbox emails)
- Python 3.12

### Step 1 — DynamoDB
- Create table: OnboardingTable
- Partition key: employeeId (String)
- Capacity: On-demand

### Step 2 — SES
- Verify sender email in SES Identities
- Request SES production access to send to any address

### Step 3 — IAM Roles
- OnboardingIntakeRole: AmazonDynamoDBFullAccess + AmazonEventBridgeFullAccess
- OnboardingNotifyRole: AmazonDynamoDBFullAccess + AmazonSESFullAccess + AmazonSNSFullAccess

### Step 4 — SNS Topic
- Create Standard topic: OnboardingManagerAlert
- Add email subscription and confirm

### Step 5 — Lambda #1
- Name: OnboardingIntake | Runtime: Python 3.12
- Attach OnboardingIntakeRole
- Deploy lambda_intake.py

### Step 6 — Lambda #2
- Name: OnboardingNotify | Runtime: Python 3.12
- Attach OnboardingNotifyRole
- Update SENDER_EMAIL and SNS_TOPIC_ARN in code
- Deploy lambda_notify.py

### Step 7 — EventBridge
- Create rule: NewHireSubmittedRule
- Event pattern: source = onboarding.system, detail-type = NewHireSubmitted
- Target: Lambda function OnboardingNotify

### Step 8 — API Gateway
- Create REST API: OnboardingAPI
- Resource: /onboard with CORS enabled
- Method: POST → Lambda proxy → OnboardingIntake
- Deploy to stage: prod

### Step 9 — Test
Send a POST request to your API endpoint with this JSON body:

    {
      "name": "John Doe",
      "email": "your@email.com",
      "department": "Engineering",
      "startDate": "2026-06-01",
      "managerEmail": "manager@email.com"
    }

Expected response:

    {
      "message": "New hire submitted successfully",
      "employeeId": "uuid-here"
    }

---

## 9. Challenges Faced

| Challenge | Resolution |
|---|---|
| SES emails landing in spam | Expected for Gmail sender addresses in test environments. Production deployments use verified business domains |
| EventBridge target not available | Lambda #2 must be deployed before creating the EventBridge rule |
| Windows SSL error with curl | Resolved with --ssl-no-revoke flag |

---

## 10. Lessons Learned

- **Decouple first** — EventBridge made this system extensible from day one. Adding a Slack notification later requires zero changes to existing Lambda functions
- **Deploy in the right order** — dependencies matter: DynamoDB → SES → IAM → SNS → Lambda #1 → Lambda #2 → EventBridge → API Gateway
- **Least privilege matters** — creating separate IAM roles per Lambda enforces security boundaries even in a small project
- **Event-driven thinking** — this project demonstrates how real enterprise HR systems work at companies like Workday and SAP

---

## Author

**Sedou Futoh**  
AWS Certified Cloud Practitioner | Junior IT Analyst  
Calgary, Alberta, Canada  
[Portfolio](https://sedoufutoh.com) | [LinkedIn](https://linkedin.com/in/sedoufutoh)
