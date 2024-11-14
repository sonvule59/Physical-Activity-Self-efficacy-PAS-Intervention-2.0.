import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string
import requests

# Function to generate a token
def generate_token(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class EmailService:
    def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    def send_email(self, recipient_email, subject, body):
        try:
            # Setting up the MIME
            message = MIMEMultipart()
            message['From'] = self.smtp_user
            message['To'] = recipient_email
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))
            
            # SMTP setup and sending the email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(message)
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

class MessagingService:
    def __init__(self, heroku_webhook_url):
        self.heroku_webhook_url = heroku_webhook_url

    def send_message(self, recipient_number, message_body):
        try:
            payload = {
                "to": recipient_number,
                "message": message_body
            }
            response = requests.post(self.heroku_webhook_url, json=payload)
            if response.status_code == 200:
                print("Message sent successfully!")
            else:
                print(f"Failed to send message, status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to send message: {str(e)}")


# Class to send emails
# class EmailService:
#     def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password):
#         self.smtp_server = smtp_server
#         self.smtp_port = smtp_port
#         self.smtp_user = smtp_user
#         self.smtp_password = smtp_password

#     def send_email(self, recipient_email, subject, body):
#         try:
#             # Setting up the MIME
#             message = MIMEMultipart()
#             message['From'] = self.smtp_user
#             message['To'] = recipient_email
#             message['Subject'] = subject
#             message.attach(MIMEText(body, 'plain'))
            
#             # SMTP setup and sending the email
#             server = smtplib.SMTP(self.smtp_server, self.smtp_port)
#             server.starttls()
#             server.login(self.smtp_user, self.smtp_password)
#             server.send_message(message)
#             server.quit()
#             print("Email sent successfully!")
#         except Exception as e:
#             print(f"Failed to send email: {str(e)}")
