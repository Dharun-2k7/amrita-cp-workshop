import random
import smtplib
from email.message import EmailMessage
from flask import current_app

def generate_otp():
    """Generates a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_otp_email(user_email, otp):
    """Sends OTP email. Uses mock printing if MOCK_EMAIL is True."""
    
    # If mock email is enabled in config, just print it to terminal
    if current_app.config['MOCK_EMAIL']:
        print("="*40)
        print(f"MOCK EMAIL SENT TO: {user_email}")
        print(f"OTP CODE: {otp}")
        print("="*40)
        return True
        
    # Real email sending using SMTP
    try:
        msg = EmailMessage()
        msg['Subject'] = 'IOI Vismaya Registration - Verify Your Email'
        msg['From'] = current_app.config['MAIL_USERNAME']
        msg['To'] = user_email
        msg.set_content(f'''Welcome to the IOI Vismaya Platform!
        
Your email verification code is: {otp}

Please enter this code on the verification page to complete your registration.
If you did not request this, please ignore this email.
''')

        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            if current_app.config['MAIL_USE_TLS']:
                server.starttls()
            server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            server.send_message(msg)
            
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
