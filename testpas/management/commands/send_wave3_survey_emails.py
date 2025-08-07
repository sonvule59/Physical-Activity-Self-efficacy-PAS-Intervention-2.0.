# testpas/management/commands/send_wave3_survey_emails.py Info 20
from django.core.management.base import BaseCommand
from testpas.models import Participant
from django.utils import timezone
import pytz

class Command(BaseCommand):
    help = 'Send Wave 3 survey emails on Day 85 at 7 AM CT'

    def handle(self, *args, **kwargs):
        ct_tz = pytz.timezone('America/Chicago')
        now = timezone.now().astimezone(ct_tz)
        today = now.date()
        day_85_participants = Participant.objects.filter(
            enrollment_date=today - timezone.timedelta(days=84)  # Day 85 = 84 days after
        )
        if now.hour >= 7:
            for participant in day_85_participants:
                participant.send_wave3_survey_email()
                self.stdout.write(self.style.SUCCESS(f"Sent Wave 3 survey email to {participant.participant_id}"))
        else:
            self.stdout.write("Not yet 7 AM CT, skipping email send.")