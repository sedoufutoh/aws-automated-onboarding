cat > lambda_notify.py << 'EOF'
import json
import boto3
from datetime import datetime, timezone

ses = boto3.client('ses', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('OnboardingTable')

SENDER_EMAIL = 'prfutohs37@gmail.com'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:332700840460:OnboardingManagerAlert'

def lambda_handler(event, context):
    try:
        detail = event['detail']
        employee_id = detail['employeeId']
        name = detail['name']
        email = detail['email']
        department = detail['department']
        start_date = detail['startDate']
        manager_email = detail['managerEmail']

        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': f'Welcome to the team, {name}!'},
                'Body': {
                    'Text': {
                        'Data': f"""Dear {name},

Welcome to the team! We are excited to have you joining us.

Here are your onboarding details:
- Department: {department}
- Start Date: {start_date}

Your manager will be in touch shortly with further instructions.

Best regards,
HR Team"""
                    }
                }
            }
        )

        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [SENDER_EMAIL]},
            Message={
                'Subject': {'Data': f'IT Provisioning Required — {name}'},
                'Body': {
                    'Text': {
                        'Data': f"""IT Team,

A new employee requires account provisioning:

- Name: {name}
- Email: {email}
- Department: {department}
- Start Date: {start_date}

Please set up all required accounts and equipment before their start date.

HR System"""
                    }
                }
            }
        )

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f'New Hire Alert — {name} joining {department}',
            Message=f"""Hello,

A new hire has been added to your team:

- Name: {name}
- Email: {email}
- Department: {department}
- Start Date: {start_date}

Please prepare for their onboarding.

HR System"""
        )

        table.update_item(
            Key={'employeeId': employee_id},
            UpdateExpression='SET #s = :status, notifiedAt = :time',
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={
                ':status': 'NOTIFIED',
                ':time': datetime.now(timezone.utc).isoformat()
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Notifications sent successfully'})
        }

    except Exception as e:
        print(f'Error: {str(e)}')
        raise e
EOF