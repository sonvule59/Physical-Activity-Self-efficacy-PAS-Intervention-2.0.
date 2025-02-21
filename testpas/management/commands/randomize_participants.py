import random
import os
from datetime import datetime, timedelta
import time
import pytz
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, BadHeaderError
from testpas import settings
from testpas.models import Participant
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail, Email, Content

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

    def send_notification_email(self, participant):
        subject = 'Group Assignment Notification'
        if participant.group == 0:
            message = f'Dear Participant {participant.participant_id},\n\nYou have been assigned to Group 0 (control group).'
        else:
            message = f'Dear Participant {participant.participant_id},\n\nYou have been assigned to Group 1 (intervention group). Your intervention period starts now and ends on {participant.intervention_end_date.strftime("%Y-%m-%d %H:%M:%S")}.'
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,  # Use DEFAULT_FROM_EMAIL from settings
                recipient_list=[participant.email],
                fail_silently=False,  # Set to True if you want to silently handle failures
            )
            self.stdout.write(self.style.SUCCESS(f"Email sent successfully to {participant.email}"))
            return True
        except BadHeaderError:
            self.stdout.write(self.style.ERROR(f'Invalid header found when sending email to {participant.email}'))
            return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sending email to {participant.email}: {e}'))
            return False
        
    def verify_randomization(self):
        total_participants = Participant.objects.count()
        randomized_participants = Participant.objects.filter(group_assigned=True).count()
        not_randomized_participants = total_participants - randomized_participants

        if not_randomized_participants == 0:
            self.stdout.write(self.style.SUCCESS("All participants are randomized."))
        else:
            self.stdout.write(self.style.WARNING(f"{not_randomized_participants} participants are not yet randomized."))