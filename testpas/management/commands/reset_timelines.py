from django.core.management.base import BaseCommand
from django.utils import timezone
from testpas.models import UserSurveyProgress

class Command(BaseCommand):
    help = 'Reset user timelines to today for testing purposes'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        updated_count = 0
        
        for progress in UserSurveyProgress.objects.filter(consent_given=True):
            progress.day_1 = today
            progress.save()
            updated_count += 1
            self.stdout.write(f"Reset timeline for user: {progress.user.username}")
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully reset timelines for {updated_count} users to {today}")
        ) 