import random
import os
from datetime import datetime, timedelta
import time
import pytz
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, BadHeaderError
from testpas import settings
from testpas.models import Participant
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, Email, Content, Subject, From, PlainTextContent

class Command(BaseCommand):
    help = 'Randomize participants into groups on Day 29 and assign access periods'
    def handle(self, *args, **kwargs):
        now = datetime.now(pytz.timezone('America/Chicago'))

        # if self.is_test_time() or (self.is_day_29() and now.hour == 7):
        if self.is_test_time() or (self.is_day_29()):
            participants = Participant.objects.filter(group_assigned=False)[:5]  # Limit to first 20 for testing
            print(f"Randomizing {len(participants)} participants...")
            for participant in participants:
                participant.group = random.choice([0, 1])  # 0 for control, 1 for intervention
                participant.group_assigned = True
                if participant.group == 1:
                    participant.intervention_start_date = now
                    participant.intervention_end_date = now + timedelta(days=27)
                participant.save()
                self.send_notification_email(participant)
                time.sleep(1)  # Sleep for 1 second to avoid rate limiting

            self.stdout.write(self.style.SUCCESS('Successfully randomized participants and sent notifications.'))
            self.verify_randomization()
        else:
            self.stdout.write('Not the correct time for randomization or not Day 29.')

    def is_day_29(self):
        # Check if today is Day 29 for the study
        # start_date = datetime(2025, 1, 1, tzinfo=pytz.timezone('America/Chicago'))
        # now = datetime.now(pytz.timezone('America/Chicago'))
        # return (now - start_date).days == 29
        return True

    def is_test_time(self):
        # Temporary function to allow testing at any time
        now = datetime.now(pytz.timezone('America/Chicago'))
        return now.minute % 2 == 0  # Allows testing every 5 minutes

    # def send_notification_email(self, participant):
    #     subject = 'Group Assignment Notification'
    #     if participant.group == 0:
    #         message = f'Dear Participant {participant.participant_id},\n\nYou have been assigned to Group 0 (control group).'
    #     else:
    #         message = f'Dear Participant {participant.participant_id},\n\nYou have been assigned to Group 1 (intervention group). Your intervention period starts now and ends on {participant.intervention_end_date.strftime("%Y-%m-%d %H:%M:%S")}.'
    #     try:
    #         send_mail(subject, message, 'sonlevu73@gmail.com', [participant.email])
    #     except BadHeaderError:
    #         self.stdout.write(self.style.ERROR(f'Invalid header found when sending email to {participant.email}'))
    #     except Exception as e:
    #         self.stdout.write(self.style.ERROR(f'Error sending email to {participant.email}: {e}'))
    def send_notification_email(self, participant):
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            
            # Add tracking and delivery confirmation
            data = {
                "personalizations": [
                    {
                        "to": [{"email": participant.email}],
                        "subject": "Group Assignment Notification"
                    }
                ],
                "from": {
                    "email": settings.DEFAULT_FROM_EMAIL,
                    "name": "PAS Project"
                },
                "tracking_settings": {
                    "click_tracking": {"enable": True},
                    "open_tracking": {"enable": True},
                    "subscription_tracking": {"enable": False},
                    "bypass_list_management": {"enable": True}
                },
                "mail_settings": {
                    "footer": {
                        "enable": True,
                        "text": "Please reply to confirm receipt of this email."
                    },
                    "bypass_spam_management": {"enable": True}
                },
                "content": [
                    {
                        "type": "text/plain",
                        "value": (f"Dear Participant {participant.participant_id},\n\n"
                                f"You have been assigned to Group {participant.group} "
                                f"({'intervention' if participant.group == 1 else 'control'} group)."
                                f"{' Your intervention period starts now and ends on ' + participant.intervention_end_date.strftime('%Y-%m-%d %H:%M:%S') if participant.group == 1 else ''}\n\n"
                                f"Best regards,\nPAS Project Team")
                    }
                ]
            }

            # Implement retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.stdout.write(f"Sending email to {participant.email} (attempt {attempt + 1})")
                    response = sg.client.mail.send.post(request_body=data)
                    
                    self.stdout.write(f"SendGrid response status code: {response.status_code}")
                    self.stdout.write(f"SendGrid response body: {response.body}")
                    self.stdout.write(f"SendGrid response headers: {response.headers}")
                    
                    if response.status_code == 202:
                        message_id = response.headers.get('X-Message-Id', 'N/A')
                        self.stdout.write(self.style.SUCCESS(
                            f"Email queued for delivery (ID: {message_id})"
                        ))
                        break  # Exit retry loop on success
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Attempt {attempt + 1} failed: {str(e)}"))
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise
                    
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to send email: {str(e)}"))
            return False

        #     subject = 'Group Assignment Notification'
        #     if participant.group == 0:
        #         message = f'Dear Participant {participant.participant_id},\n\nYou have been assigned to Group 0 (control group).'
        #     else:
        #         message = f'Dear Participant {participant.participant_id},\n\nYou have been assigned to Group 1 (intervention group). Your intervention period starts now and ends on {participant.intervention_end_date.strftime("%Y-%m-%d %H:%M:%S")}.'
            
        #     content = Mail(
        #         from_email=From(settings.DEFAULT_FROM_EMAIL),
        #         to_emails=To(participant.email),
        #         subject=Subject('Group Assignment Notification'),
        #         plain_text_content=PlainTextContent(message)
        #     )
        #     # Send email
        #     self.stdout.write(f"Sending email to {participant.email}")
        #     response = sg.send(email)
            
        #     if response.status_code == 202:
        #         self.stdout.write(self.style.SUCCESS(f"Email sent successfully to {participant.email}"))
        #         return True
        #     else:
        #         self.stdout.write(self.style.ERROR(f"Failed to send email: {response.body}"))
        #         return False
            
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f"SendGrid error: {str(e)}"))
        #     return False
        # try:
        #     api_key_preview = f"{settings.SENDGRID_API_KEY[:5]}...{settings.SENDGRID_API_KEY[-5:]}"
        #     self.stdout.write(f"Using API key: {api_key_preview}")
        #     self.stdout.write(f"Sending email to {participant.email}")
        #     sg = SendGridAPIClient(settings.SENDGRID_API_KEY)  # Replace with your new SendGrid API key
        #     response = sg.send(message)
        #     self.stdout.write(f"Email sent to {participant.email}, status code: {response.status_code}")
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f"Error sending email to {participant.email}: {e}"))
        
    def verify_randomization(self):
        total_participants = Participant.objects.count()
        randomized_participants = Participant.objects.filter(group_assigned=True).count()
        not_randomized_participants = total_participants - randomized_participants

        if not_randomized_participants == 0:
            self.stdout.write(self.style.SUCCESS("All participants are randomized."))
        else:
            self.stdout.write(self.style.WARNING(f"{not_randomized_participants} participants are not yet randomized."))