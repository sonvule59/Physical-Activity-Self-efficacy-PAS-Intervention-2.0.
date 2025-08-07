# testpas/management/commands/send_wave3_missing_code_emails.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from testpas.models import Participant

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        participants = Participant.objects.filter(
            wave3_code_entered=False,
            enrollment_date=today - timezone.timedelta(days=103)
        ).exclude(email_status='sent')
        for p in participants:
            p.send_wave3_missing_code_email()  # Info 25
            self.stdout.write(f"Sent Wave 3 missing code email to {p.user.username}")