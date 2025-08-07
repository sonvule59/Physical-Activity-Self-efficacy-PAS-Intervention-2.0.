# testpas/management/commands/send_study_end_emails.py - INFO 24    
from django.core.management.base import BaseCommand
from testpas.models import Participant
from django.utils import timezone
import pytz

class Command(BaseCommand):
    help = 'Send study end emails 8 days after Wave 3 code entry at 7 AM CT'

    def handle(self, *args, **kwargs):
        ct_tz = pytz.timezone('America/Chicago')
        now = timezone.now().astimezone(ct_tz)
        today = now.date()
        day_8_participants = Participant.objects.filter(
            wave3_code_entered=True,
            wave3_code_entry_date=today - timezone.timedelta(days=7)  # 8th day = 7 days after
        )
        if now.hour >= 7:
            for participant in day_8_participants:
                participant.send_study_end_email()
                self.stdout.write(self.style.SUCCESS(f"Sent study end email to {participant.participant_id}"))
        else:
            self.stdout.write("Not yet 7 AM CT, skipping email send.")