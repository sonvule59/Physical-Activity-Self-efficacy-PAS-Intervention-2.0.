# testpas/management/commands/send_wave2_no_monitoring_emails.py
from django.core.management.base import BaseCommand
from testpas.models import Participant
from django.utils import timezone
import pytz

class Command(BaseCommand):
    help = 'Send Wave 2 no monitoring emails on Day 67 at 7 AM CT'

    def handle(self, *args, **kwargs):
        ct_tz = pytz.timezone('America/Chicago')
        now = timezone.now().astimezone(ct_tz)
        today = now.date()
        day_67_participants = Participant.objects.filter(
            enrollment_date=today - timezone.timedelta(days=66)  # Day 67 = 66 days after
        )
        if now.hour >= 7:
            for participant in day_67_participants:
                participant.send_wave2_no_monitoring_email()
                self.stdout.write(self.style.SUCCESS(f"Sent Wave 2 no monitoring email to {participant.participant_id}"))
        else:
            self.stdout.write("Not yet 7 AM CT, skipping email send.")