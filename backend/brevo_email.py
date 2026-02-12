import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Configure API key - PASTE YOUR BREVO API KEY HERE
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.environ.get('BREVO_API_KEY', '')  # ✅ READ FROM ENV
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

def send_test_alert():
    """Send test email to srinithiyadevops@gmail.com"""
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": "srinithiyadevops@gmail.com", "name": "Srinithiya"}],
        sender={"email": "srinithiyadevops@gmail.com", "name": "CloudOptima"},
        subject="🚀 CloudOptima Phase 2 - Auto Alert Working!",
        html_content="""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #f9fafb; padding: 30px; border-radius: 10px;">
                <div style="background: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0;">⚡ CloudOptima</h1>
                </div>
                <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #1e293b;">✅ Auto-Alert System Working!</h2>
                    <p style="font-size: 16px; color: #475569;">Hi Srinithiya,</p>
                    <p style="font-size: 16px; color: #475569;">This is a test email from your CloudOptima Phase 2 implementation.</p>
                    <div style="background: #f1f5f9; padding: 20px; border-left: 4px solid #2563eb; margin: 20px 0;">
                        <p style="margin: 0; color: #0f172a;"><strong>📧 Email Service:</strong> Brevo (Sendinblue)</p>
                        <p style="margin: 10px 0 0 0; color: #0f172a;"><strong>🔧 Status:</strong> Working ✅</p>
                    </div>
                    <p style="color: #475569;">Your Phase 2 is ready! The system will now automatically:</p>
                    <ul style="color: #475569;">
                        <li>🔍 Scan AWS every 6 hours</li>
                        <li>💤 Detect idle resources</li>
                        <li>📧 Send alerts to resource owners</li>
                    </ul>
                    <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 14px;">
                        This is an automated test from your CloudOptima backend.<br>
                        Project Phase 2 - Multi-Cloud Cost Optimization
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    )
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Email sent successfully!")
        print(f"📋 Message ID: {api_response.message_id}")
        return True
    except ApiException as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Sending CloudOptima Phase 2 test email...")
    send_test_alert()
