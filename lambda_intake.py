cat > lambda_intake.py << 'EOF'
import json
import boto3
import uuid
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('OnboardingTable')

eventbridge = boto3.client('events')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))

        required_fields = ['name', 'email', 'department', 'startDate', 'managerEmail']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }

        employee_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        table.put_item(Item={
            'employeeId': employee_id,
            'name': body['name'],
            'email': body['email'],
            'department': body['department'],
            'startDate': body['startDate'],
            'managerEmail': body['managerEmail'],
            'status': 'PENDING',
            'createdAt': created_at
        })

        eventbridge.put_events(
            Entries=[
                {
                    'Source': 'onboarding.system',
                    'DetailType': 'NewHireSubmitted',
                    'Detail': json.dumps({
                        'employeeId': employee_id,
                        'name': body['name'],
                        'email': body['email'],
                        'department': body['department'],
                        'startDate': body['startDate'],
                        'managerEmail': body['managerEmail']
                    }),
                    'EventBusName': 'default'
                }
            ]
        )

        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'message': 'New hire submitted successfully',
                'employeeId': employee_id
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
EOF