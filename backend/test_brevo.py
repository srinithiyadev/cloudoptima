from brevo_email import send_test_alert

print("🚀 Sending test email...")
result = send_test_alert()

if result:
    print("✅ Email sent! Check your inbox.")
else:
    print("❌ Failed. Check API key.")
