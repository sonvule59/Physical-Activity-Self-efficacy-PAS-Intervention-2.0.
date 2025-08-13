from django.core.management.base import BaseCommand
from django.utils import timezone
from testpas.models import UserSurveyProgress, Participant
from datetime import datetime

class Command(BaseCommand):
    help = 'Reset participant timelines to current moment for time compression testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--participant',
            type=str,
            help='Specific participant ID to reset (optional)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Reset all participants'
        )

    def handle(self, *args, **options):
        current_time = timezone.now()
        
        if options['participant']:
            participants = Participant.objects.filter(participant_id=options['participant'])
        elif options['all']:
            participants = Participant.objects.all()
        else:
            # Default: reset the most recent participant
            participants = Participant.objects.order_by('-id')[:1]
        
        if not participants.exists():
            self.stdout.write(self.style.WARNING("No participants found to reset."))
            return
        
        for participant in participants:
            # Get user progress
            user_progress = UserSurveyProgress.objects.filter(
                user=participant.user, 
                survey__title="Eligibility Criteria"
            ).first()
            
            if user_progress:
                old_day_1 = user_progress.day_1
                # Set day_1 to current date and time for proper time compression
                user_progress.day_1 = current_time.date()
                user_progress.timeline_reference_timestamp = current_time
                user_progress.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Reset timeline for {participant.participant_id} "
                        f"({participant.user.username}): "
                        f"Day 1 changed from {old_day_1} to {user_progress.day_1} "
                        f"at {current_time.strftime('%H:%M:%S')}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"No progress record found for {participant.participant_id}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Timeline reset complete. Participants can now be tested with "
                f"time compression (10 seconds per day). Study Day 1 starts now!"
            )
        ) 