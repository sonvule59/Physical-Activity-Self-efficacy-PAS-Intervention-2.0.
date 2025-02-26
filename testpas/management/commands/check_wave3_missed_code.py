# testpas/management/commands/check_wave3_missed_code.py - info 25
from django.core.management.base import BaseCommand
from testpas.models import Participant
from django.conf import settings
from django.utils import timezone
import pytz
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Check and send emails for missed Wave 3 code entry on Day 105'

    def handle(self, *args, **kwargs):
        ct_tz = pytz.timezone('America/Chicago')
        now = timezone.now().astimezone(ct_tz)
        today = now.date()
        day_105_participants = Participant.objects.filter(
            enrollment_date=today - timezone.timedelta(days=104),
            code_entered=False  # Assumes reuse; adjust if wave-specific field added
        )
        if now.hour >= 7:
            for participant in day_105_participants:
                send_mail(
                    "Missed Wave 3 Code Entry",
                    f"Hi {participant.participant_id},\n\nYou did not enter the Wave 3 code.",
                    settings.DEFAULT_FROM_EMAIL,
                    [participant.user.email, 'svu23@iastate.edu'],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f"Sent missed Wave 3 code email to {participant.participant_id}"))
        else:
            self.stdout.write("Not yet 7 AM CT, skipping email send.")