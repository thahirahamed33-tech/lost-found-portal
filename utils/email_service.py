# Email Service for CampusLost
# Uses Gmail SMTP with App Password authentication

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================================
# SMTP Configuration
# ========================================

class EmailConfig:
    """Email configuration settings"""
    
    # Gmail SMTP Settings
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT_SSL = 465  # SSL port
    SMTP_PORT_TLS = 587  # TLS port
    SMTP_USERNAME = os.environ.get('GMAIL_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', '')  # App password, not regular password
    
    # Sender info
    SENDER_NAME = 'CampusLost Portal'
    SENDER_EMAIL = os.environ.get('GMAIL_SENDER_EMAIL', '')
    
    # Enable/Disable email sending (for testing)
    EMAIL_ENABLED = os.environ.get('EMAIL_ENABLED', 'False').lower() == 'true'
    
    # Use TLS instead of SSL
    USE_TLS = True
    
    @classmethod
    def is_configured(cls):
        """Check if email is properly configured"""
        return bool(cls.SMTP_USERNAME and cls.SMTP_PASSWORD and cls.SENDER_EMAIL)


# ========================================
# Email Templates
# ========================================

def get_claim_approved_html(item_name, claimant_name):
    """HTML template for claim approval"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 30px; text-align: center; }}
            .header h1 {{ color: #ffffff; margin: 0; font-size: 28px; }}
            .content {{ padding: 30px; }}
            .status-badge {{ display: inline-block; background: #00d9a5; color: white; padding: 8px 20px; border-radius: 25px; font-weight: bold; margin: 10px 0; }}
            .item-card {{ background: #f8f9fa; border-left: 4px solid #00d9a5; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .item-name {{ font-size: 18px; font-weight: bold; color: #1a1a2e; margin-bottom: 5px; }}
            .instructions {{ background: #e8f5e9; border: 1px solid #c8e6c9; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ background: #f4f4f4; padding: 20px; text-align: center; color: #666; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎓 CampusLost</h1>
            </div>
            <div class="content">
                <h2 style="color: #1a1a2e;">Great News, {claimant_name}!</h2>
                <span class="status-badge">✅ CLAIM APPROVED</span>
                
                <div class="item-card">
                    <div class="item-name">{item_name}</div>
                    <div style="color: #666;">Your claim has been approved!</div>
                </div>
                
                <div class="instructions">
                    <strong>📍 Next Steps:</strong>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>Contact the item owner to arrange a meeting</li>
                        <li>Bring proof of ownership when meeting</li>
                        <li>Return to the campus lost & found office if needed</li>
                    </ul>
                </div>
                
                <p style="color: #666;">If you have any questions, please contact the admin team.</p>
            </div>
            <div class="footer">
                <p>CampusLost - College Lost & Found Portal</p>
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_claim_rejected_html(item_name, claimant_name, reason=""):
    """HTML template for claim rejection"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 30px; text-align: center; }}
            .header h1 {{ color: #ffffff; margin: 0; font-size: 28px; }}
            .content {{ padding: 30px; }}
            .status-badge {{ display: inline-block; background: #e94560; color: white; padding: 8px 20px; border-radius: 25px; font-weight: bold; margin: 10px 0; }}
            .item-card {{ background: #f8f9fa; border-left: 4px solid #e94560; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .item-name {{ font-size: 18px; font-weight: bold; color: #1a1a2e; margin-bottom: 5px; }}
            .reason {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ background: #f4f4f4; padding: 20px; text-align: center; color: #666; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎓 CampusLost</h1>
            </div>
            <div class="content">
                <h2 style="color: #1a1a2e;">Hello, {claimant_name}</h2>
                <span class="status-badge">❌ CLAIM REJECTED</span>
                
                <div class="item-card">
                    <div class="item-name">{item_name}</div>
                    <div style="color: #666;">Unfortunately, your claim was not approved.</div>
                </div>
                {f'<div class="reason"><strong>Reason:</strong> {reason}</div>' if reason else ''}
                
                <div style="margin-top: 20px;">
                    <p style="color: #666;">If you believe this is an error, please:</p>
                    <ul style="color: #666; padding-left: 20px;">
                        <li>Contact the admin team for more information</li>
                        <li>Submit a new claim with additional proof</li>
                        <li>Visit the lost & found office in person</li>
                    </ul>
                </div>
            </div>
            <div class="footer">
                <p>CampusLost - College Lost & Found Portal</p>
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_claim_approved_plain(item_name, claimant_name):
    """Plain text template for claim approval"""
    return f"""
    🎓 CampusLost - Claim Approved
    
    Hello {claimant_name},
    
    Great news! Your claim for "{item_name}" has been APPROVED!
    
    Next Steps:
    1. Contact the item owner to arrange a meeting
    2. Bring proof of ownership when meeting
    3. Return to the campus lost & found office if needed
    
    ---
    CampusLost - College Lost & Found Portal
    """


def get_claim_rejected_plain(item_name, claimant_name, reason=""):
    """Plain text template for claim rejection"""
    return f"""
    🎓 CampusLost - Claim Status Update
    
    Hello {claimant_name},
    
    Unfortunately, your claim for "{item_name}" has been rejected.
    {f'Reason: {reason}' if reason else ''}
    
    If you believe this is an error, please:
    - Contact the admin team for more information
    - Submit a new claim with additional proof
    - Visit the lost & found office in person
    
    ---
    CampusLost - College Lost & Found Portal
    """


# ========================================
# Email Service Class
# ========================================

class EmailService:
    """Service class for sending emails via Gmail SMTP"""
    
    def __init__(self):
        self.config = EmailConfig()
    
    def send_email(self, to_email, subject, html_content, plain_content=None):
        """
        Send an email via Gmail SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML formatted email body
            plain_content: Plain text fallback (optional)
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Check if email is enabled
        if not self.config.EMAIL_ENABLED:
            logger.info(f"Email disabled. Would send to {to_email}: {subject}")
            return True
        
        # Check configuration
        if not self.config.is_configured():
            logger.error("Email not configured. Set GMAIL_USERNAME, GMAIL_APP_PASSWORD, and GMAIL_SENDER_EMAIL")
            return False
        
        if not plain_content:
            plain_content = "Please view this email in an HTML-enabled client."
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config.SENDER_NAME} <{self.config.SENDER_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # Attach plain and HTML versions
            part1 = MIMEText(plain_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Connect to Gmail and send
            if self.config.USE_TLS:
                # Use TLS on port 587
                server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT_TLS)
                server.starttls()
                server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
                server.sendmail(
                    self.config.SENDER_EMAIL,
                    to_email,
                    msg.as_string()
                )
                server.quit()
            else:
                # Use SSL on port 465
                with smtplib.SMTP_SSL(self.config.SMTP_SERVER, self.config.SMTP_PORT_SSL) as server:
                    server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
                    server.sendmail(
                        self.config.SENDER_EMAIL,
                        to_email,
                        msg.as_string()
                    )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {str(e)}")
            print(f"DEBUG - Auth Error: {e.smtp_error}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP Error: {str(e)}")
            print(f"DEBUG - SMTP Error: {e.smtp_error}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            print(f"DEBUG - Error: {type(e).__name__}: {e}")
            return False
    
    def send_claim_approved(self, to_email, claimant_name, item_name):
        """Send claim approval notification"""
        subject = f"🎓 CampusLost - Your claim for '{item_name}' has been approved!"
        
        html = get_claim_approved_html(item_name, claimant_name)
        plain = get_claim_approved_plain(item_name, claimant_name)
        
        return self.send_email(to_email, subject, html, plain)
    
    def send_claim_rejected(self, to_email, claimant_name, item_name, reason=""):
        """Send claim rejection notification"""
        subject = f"🎓 CampusLost - Your claim for '{item_name}' has been rejected"
        
        html = get_claim_rejected_html(item_name, claimant_name, reason)
        plain = get_claim_rejected_plain(item_name, claimant_name, reason)
        
        return self.send_email(to_email, subject, html, plain)


# ========================================
# Singleton Instance
# ========================================

# Create global email service instance
email_service = EmailService()


# ========================================
# Helper Functions
# ========================================

def send_claim_notification(claim_id, status, reason=""):
    """
    Send email notification for claim status change
    
    Args:
        claim_id: ID of the claim
        status: 'approved' or 'rejected'
        reason: Optional reason for rejection
    
    Returns:
        bool: True if email sent successfully
    """
    from models.database import get_db_connection
    
    connection = get_db_connection()
    if not connection:
        logger.error("Database connection failed")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Get claim details with user and item info
        cursor.execute("""
            SELECT c.id, c.user_id, c.status, i.name as item_name, u.name as user_name, u.email as user_email
            FROM claims c
            JOIN items i ON c.item_id = i.id
            JOIN users u ON c.user_id = u.id
            WHERE c.id = ?
        """, (claim_id,))
        
        claim = cursor.fetchone()
        
        if not claim:
            logger.error(f"Claim {claim_id} not found")
            return False
        
        # Send appropriate email
        if status == 'approved':
            return email_service.send_claim_approved(
                claim['user_email'],
                claim['user_name'],
                claim['item_name']
            )
        elif status == 'rejected':
            return email_service.send_claim_rejected(
                claim['user_email'],
                claim['user_name'],
                claim['item_name'],
                reason
            )
        else:
            logger.error(f"Invalid status: {status}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending claim notification: {str(e)}")
        return False
    finally:
        cursor.close()
        connection.close()


# ========================================
# Test Function
# ========================================

def test_email_config():
    """Test email configuration"""
    print("=" * 50)
    print("CampusLost Email Configuration Test")
    print("=" * 50)
    print(f"SMTP Server: {EmailConfig.SMTP_SERVER}:{EmailConfig.SMTP_PORT}")
    print(f"Username: {EmailConfig.SMTP_USERNAME}")
    print(f"Sender Email: {EmailConfig.SENDER_EMAIL}")
    print(f"Email Enabled: {EmailConfig.EMAIL_ENABLED}")
    print(f"Is Configured: {EmailConfig.is_configured()}")
    print("=" * 50)
    
    if EmailConfig.is_configured():
        print("\n✅ Email configuration looks good!")
        print("\nTo send a test email, run:")
        print("  from utils.email_service import email_service")
        print("  email_service.send_email('test@example.com', 'Test', '<h1>Test</h1>', 'Test')")
    else:
        print("\n❌ Email not configured!")
        print("\nRequired environment variables:")
        print("  GMAIL_USERNAME=your-email@gmail.com")
        print("  GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx")
        print("  GMAIL_SENDER_EMAIL=your-email@gmail.com")
        print("  EMAIL_ENABLED=True")


if __name__ == '__main__':
    test_email_config()
