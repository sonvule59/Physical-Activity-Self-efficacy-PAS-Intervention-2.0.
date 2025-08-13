from django.core.management.base import BaseCommand
from testpas.models import UserSurveyProgress, Participant
from testpas.utils import get_current_time
from testpas.timeline import get_study_day
from testpas import settings
import time

class Command(BaseCommand):
    help = 'Test timeline calculation and email automation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--participant',
            type=str,
            default='P034',
            help='Participant ID to test'
        )

    def handle(self, *args, **options):
        participant_id = options['participant']
        
        try:
            participant = Participant.objects.get(participant_id=participant_id)
            user_progress = UserSurveyProgress.objects.filter(
                user=participant.user, 
                survey__title="Eligibility Criteria"
            ).first()
            
            if not user_progress:
                self.stdout.write(self.style.ERROR(f"No progress found for {participant_id}"))
                return
            
            self.stdout.write(f"Testing timeline for participant: {participant_id}")
            self.stdout.write(f"Username: {participant.user.username}")
            self.stdout.write(f"Day 1: {user_progress.day_1}")
            self.stdout.write(f"Time Compression: {settings.TIME_COMPRESSION}")
            self.stdout.write(f"Seconds per day: {settings.SECONDS_PER_DAY}")
            
            # Test timeline calculation
            current_time = get_current_time()
            study_day = get_study_day(
                user_progress.day_1,
                now=current_time,
                compressed=settings.TIME_COMPRESSION,
                seconds_per_day=settings.SECONDS_PER_DAY,
                reference_timestamp=user_progress.timeline_reference_timestamp
            )
            
            self.stdout.write(f"Current time: {current_time}")
            self.stdout.write(f"Calculated study day: {study_day}")
            
            # Check what should happen
            if study_day == 1:
                self.stdout.write(self.style.SUCCESS("→ Should send Wave 1 survey email"))
            elif study_day == 11:
                self.stdout.write(self.style.SUCCESS("→ Should send Wave 1 monitoring email"))
            elif study_day == 21:
                self.stdout.write(self.style.SUCCESS("→ Should send Wave 1 missing code email"))
            elif study_day == 29:
                self.stdout.write(self.style.SUCCESS("→ Should randomize participant"))
            elif study_day == 57:
                self.stdout.write(self.style.SUCCESS("→ Should send Wave 2 survey email"))
            elif study_day == 85:
                self.stdout.write(self.style.SUCCESS("→ Should send Wave 3 survey email"))
            elif study_day == 95:
                self.stdout.write(self.style.SUCCESS("→ Should send Wave 3 monitoring email"))
            elif study_day == 105:
                self.stdout.write(self.style.SUCCESS("→ Should send study end email"))
            else:
                self.stdout.write(f"→ No specific email scheduled for day {study_day}")
            
            # Test timeline progression
            self.stdout.write("\nTesting timeline progression:")
            for i in range(5):
                time.sleep(2)  # Wait 2 seconds
                current_time = get_current_time()
                study_day = get_study_day(
                    user_progress.day_1,
                    now=current_time,
                    compressed=settings.TIME_COMPRESSION,
                    seconds_per_day=settings.SECONDS_PER_DAY
                )
                self.stdout.write(f"  After {i+1} intervals: Study Day {study_day}")
            
        except Participant.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Participant {participant_id} not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}")) 