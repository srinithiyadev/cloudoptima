import os
from dotenv import load_dotenv
# Load .env file - THIS IS CRITICAL!
load_dotenv()

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Get API key from environment
api_key = os.environ.get('BREVO_API_KEY')
print(f"🔑 API Key loaded: {'Yes' if api_key else 'No'}")  # Debug line

if not api_key:
    print("❌ ERROR: BREVO_API_KEY not found in .env file!")
    exit(1)

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = api_key

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

def send_test_alert():
    """Send test email to srinithiyadevops@gmail.com"""
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": "srinithiyadevops@gmail.com", "name": "Srinithiya"}],
        sender={"email": "srinithiyadevops@gmail.com", "name": "CloudOptima"},
        subject="🚀 CloudOptima Test Alert",
        html_content="<h2>Test Email</h2><p>If you see this, Brevo is working!</p>"
    )
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Email sent successfully!")
        return True
    except ApiException as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Sending test email...")
    send_test_alert()
