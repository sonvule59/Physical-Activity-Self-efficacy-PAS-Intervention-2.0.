from django.core.management.base import BaseCommand
from testpas.models import Participant, ParticipantEntry
from django.utils import timezone
from datetime import timedelta
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        participants = Participant.objects.filter(
            code_entered=True,
            code_entry_date=today - timedelta(days=8)
            # email_status__ne='sent'
        ).exclude(email_status='sent')
        for p in participants:
            p.send_wave1_survey_return_email()
            self.stdout.write(f"Sent email to {p.user.username}")