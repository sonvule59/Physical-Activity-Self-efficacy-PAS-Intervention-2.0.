# management/commands/send_missing_code_emails.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from testpas.models import Participant

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        participants = Participant.objects.filter(
            code_entered=False,
            enrollment_date=today - timezone.timedelta(days=20)
        ).exclude(email_status='sent')  # Fixed
        for p in participants:
            p.send_missing_code_email()
            self.stdout.write(f"Sent email to {p.user.username}")