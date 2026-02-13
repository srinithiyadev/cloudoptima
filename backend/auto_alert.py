import os
from dotenv import load_dotenv
load_dotenv()

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from datetime import datetime
import boto3

# Initialize Brevo
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.environ.get('BREVO_API_KEY')
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

def scan_aws_idle_resources():
    """Scan AWS for idle resources"""
    idle_resources = []
    
    try:
        # Connect to AWS
        ec2 = boto3.client('ec2', region_name='us-east-1')
        
        # Get all EC2 instances
        instances = ec2.describe_instances()
        
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                # Skip if instance is running (simplified check)
                if instance['State']['Name'] == 'running':
                    # Check tags for owner email
                    owner_email = None
                    if 'Tags' in instance:
                        for tag in instance['Tags']:
                            if tag['Key'] == 'Owner':
                                owner_email = tag['Value']
                    
                    # If no owner tag, use default
                    if not owner_email:
                        owner_email = 'srinithiyadevops@gmail.com'
                    
                    # Add to idle list (simplified - you can add CPU check)
                    idle_resources.append({
                        'id': instance['InstanceId'],
                        'name': next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'Unnamed'),
                        'type': 'EC2',
                        'region': instance['Placement']['AvailabilityZone'],
                        'owner': owner_email,
                        'idle_days': 7,  # Placeholder
                        'monthly_cost': 45.50  # Placeholder
                    })
        
        return idle_resources
    except Exception as e:
        print(f"Error scanning AWS: {e}")
        return []

def send_alert_email(owner_email, resource):
    """Send alert email for idle resource"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #f9fafb; padding: 30px; border-radius: 10px;">
            <div style="background: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h2>⚡ CloudOptima Auto-Alert</h2>
            </div>
            <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px;">
                <h3>Idle Resource Detected!</h3>
                
                <div style="background: #fef2f2; padding: 20px; border-left: 4px solid #ef4444; margin: 20px 0;">
                    <p><strong>Resource:</strong> {resource['name']} ({resource['id']})</p>
                    <p><strong>Type:</strong> {resource['type']}</p>
                    <p><strong>Region:</strong> {resource['region']}</p>
                    <p><strong>Idle for:</strong> {resource['idle_days']} days</p>
                    <p><strong>Estimated Monthly Waste:</strong> ${resource['monthly_cost']}</p>
                </div>
                
                <p>This resource appears to be idle and is costing you money.</p>
                <p>Please log in to AWS Console to review and terminate if not needed.</p>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="https://console.aws.amazon.com" style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">View in AWS Console</a>
                </div>
                
                <p style="margin-top: 30px; font-size: 12px; color: #666;">
                    This is an automated alert from CloudOptima.<br>
                    To stop receiving these alerts, tag your resource with 'OptOut: true'
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": owner_email}],
        sender={"email": "srinithiyadevops@gmail.com", "name": "CloudOptima"},
        subject=f"⚠️ Idle Resource: {resource['name']}",
        html_content=html_content
    )
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Alert sent to {owner_email}")
        return True
    except ApiException as e:
        print(f"❌ Error: {e}")
        return False

def run_auto_scan():
    """Main function to scan and alert"""
    print(f"🔍 Starting auto-scan at {datetime.now()}")
    
    # Scan AWS
    idle_resources = scan_aws_idle_resources()
    
    if not idle_resources:
        print("✅ No idle resources found")
        return
    
    print(f"📊 Found {len(idle_resources)} idle resources")
    
    # Send alerts
    for resource in idle_resources:
        send_alert_email(resource['owner'], resource)
    
    print(f"✅ Auto-scan completed at {datetime.now()}")

if __name__ == "__main__":
    run_auto_scan()
def test_with_sample_data():
    """Send test alert with sample data"""
    sample_resource = {
        'id': 'i-1234567890abcdef',
        'name': 'test-server',
        'type': 'EC2',
        'region': 'us-east-1a',
        'owner': 'srinithiyadevops@gmail.com',
        'idle_days': 15,
        'monthly_cost': 45.50
    }
    
    print("📧 Sending test alert email...")
    send_alert_email('srinithiyadevops@gmail.com', sample_resource)

# Add this at the bottom to run test
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_with_sample_data()
    else:
        run_auto_scan()
