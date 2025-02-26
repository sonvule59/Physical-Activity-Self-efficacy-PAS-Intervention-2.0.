# testpas/management/commands/send_wave2_emails.py
from django.core.management.base import BaseCommand
from testpas.models import Participant
from django.utils import timezone
import pytz

class Command(BaseCommand):
    help = 'Send Wave 2 survey emails to participants on Day 57 at 7 AM CT'

    def handle(self, *args, **kwargs):
        ct_tz = pytz.timezone('America/Chicago')
        now = timezone.now().astimezone(ct_tz)
        today = now.date()
        
        # Day 57 is 56 days after enrollment_date (since Day 1 is the enrollment day)
        day_57_participants = Participant.objects.filter(
            enrollment_date=today - timezone.timedelta(days=56)
        )

        if now.hour >= 7:  # Send at or after 7 AM CT
            for participant in day_57_participants:
                participant.send_wave2_survey_email()
                self.stdout.write(self.style.SUCCESS(f"Sent Wave 2 email to {participant.participant_id}"))
        else:
            self.stdout.write("Not yet 7 AM CT, skipping email send.")