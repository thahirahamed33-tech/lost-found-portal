#!/usr/bin/env python
"""
Email Configuration Test Script
Run this to test your Gmail SMTP settings
"""
import os
import sys

# Set environment variables (for testing - in production use .env file)
os.environ['GMAIL_USERNAME'] = 'lostandfoundportal33@gmail.com'
os.environ['GMAIL_APP_PASSWORD'] = 'qesezbuyvihlnjdk'
os.environ['GMAIL_SENDER_EMAIL'] = 'lostandfoundportal33@gmail.com'
os.environ['EMAIL_ENABLED'] = 'True'

# Now import the email service
from utils.email_service import EmailConfig, email_service

print("=" * 60)
print("CampusLost Email Configuration Test")
print("=" * 60)
print()

# Check configuration
print("Configuration:")
port = EmailConfig.SMTP_PORT_TLS if EmailConfig.USE_TLS else EmailConfig.SMTP_PORT_SSL
print(f"  SMTP Server: {EmailConfig.SMTP_SERVER}:{port}")
print(f"  Username: {EmailConfig.SMTP_USERNAME}")
print(f"  Password set: {'Yes' if EmailConfig.SMTP_PASSWORD else 'No'}")
print(f"  Sender: {EmailConfig.SENDER_EMAIL}")
print(f"  Email Enabled: {EmailConfig.EMAIL_ENABLED}")
print(f"  Is Configured: {EmailConfig.is_configured()}")
print()

# Test sending email
if EmailConfig.is_configured():
    print("Attempting to send test email...")
    print()
    
    # Send test email
    result = email_service.send_email(
        to_email='lostandfoundportal33@gmail.com',
        subject='CampusLost - Test Email from Flask App',
        html_content="""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1 style="color: #1a1a2e;">🎓 CampusLost Test</h1>
            <p>This is a test email to verify your Gmail SMTP configuration is working!</p>
            <p>If you receive this, your email settings are correct.</p>
        </body>
        </html>
        """,
        plain_content="CampusLost Test - If you receive this, your email settings are correct."
    )
    
    if result:
        print("✅ SUCCESS: Test email sent!")
        print("   Check your Gmail inbox (and spam folder)")
    else:
        print("❌ FAILED: Email was not sent")
        print("   Check the error messages above")
else:
    print("❌ Email not configured!")
    print("   Set these environment variables:")
    print("   - GMAIL_USERNAME")
    print("   - GMAIL_APP_PASSWORD")
    print("   - GMAIL_SENDER_EMAIL")
    print("   - EMAIL_ENABLED=True")

print()
print("=" * 60)
