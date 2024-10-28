import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_verification_email(recipient_email, subject, body):
    sender_email = current_app.config['MAIL_USERNAME']
    sender_password = current_app.config['MAIL_PASSWORD']
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Establish secure connection with server and send the email
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        print("Verification email sent!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")