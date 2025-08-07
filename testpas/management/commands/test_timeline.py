from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from django.utils import timezone
from freezegun import freeze_time
import time
from testpas.models import Participant, UserSurveyProgress, Survey


class Command(BaseCommand):
    help = "Run compressed timeline simulation for a participant"

    def add_arguments(self, parser):
        parser.add_argument(
            '--participant-id',
            type=str,
            default='P001',
            help='Participant ID to simulate'
        )
        parser.add_argument(
            '--speed',
            type=float,
            default=1.0,
            help='Speed multiplier for simulation'
        )

    def setup_participant(self):
        if User.objects.filter(username='testuser_sonvu1').exists():
            User.objects.filter(username='testuser_sonvu1').delete()
            self.stdout.write("Deleted existing 'testuser_sonvu' to avoid UNIQUE constraint error.")
        if Participant.objects.filter(participant_id='P001').exists():
            Participant.objects.filter(participant_id='P001').delete()
            self.stdout.write("Deleted existing participant 'P001' to avoid UNIQUE constraint error.")
        user = User.objects.create_user(username='testuser_sonvu1', email='vuleson59@gmail.com', password='testpass')
        survey = Survey.objects.create(title="Eligibility Survey", description="Test survey")
        participant = Participant.objects.create(
            user=user,
            email=user.email,
            phone_number='1234567890',
            enrollment_date=timezone.datetime(2025, 4, 3).date(),
            participant_id='P001',
            code_entered=False,
            wave3_code_entered=False,
            wave3_code_entry_date=None,
            group_assigned=False,
            intervention_start_date=None,
            intervention_end_date=None,
            confirmation_token='testtoken',
            email_send_date=None
        )
        UserSurveyProgress.objects.create(
            user=user,
            survey=survey,
            eligible=True,
            consent_given=True,
            day_1=timezone.datetime(2025, 4, 3).date()
        )
        return participant

    def handle(self, *args, **options):
        participant_id = options['participant_id']
        speed = options['speed']
        self.stdout.write(f"Running simulation for participant {participant_id} with speed {speed}")

        # Fetch or create participant
        try:
            participant = Participant.objects.get(participant_id=participant_id)
        except Participant.DoesNotExist:
            self.stdout.write(f"Participant {participant_id} not found, creating new one...")
            participant = self.setup_participant()

        base_date = participant.enrollment_date

        events = {
            10: "Day 11 - Wave 1 code entry available",
            20: "Day 21 - Check Wave 1 code entry",
            28: "Day 29 - Randomization",
            56: "Day 57 - Wave 2 survey ready",
            66: "Day 67 - No Wave 2 monitoring",
            84: "Day 85 - Wave 3 survey ready",
            94: "Day 95 - Wave 3 monitoring ready",
            103: "Day 104 - Check Wave 3 code entry",
            111: "Day 112 - Data export"
        }

        for day in range(112):
            with freeze_time(base_date + timezone.timedelta(days=day)):
                current_date = timezone.now().date()
                self.stdout.write(f"Simulated Date: {current_date} (Day {day})")

                if day in events:
                    self.stdout.write(f"Event: {events[day]}")

                if day == 10:
                    participant.code_entered = True
                    participant.code_entry_date = current_date
                    participant.save()
                    participant.send_code_entry_email()
                    self.stdout.write("Wave 1 code entered")

                if day == 18:
                    call_command('send_wave1_survey_emails')

                if day == 20:
                    call_command('send_missing_code_emails')

                if day == 28:
                    call_command('randomize_participants')

                if day == 56:
                    call_command('send_wave2_survey_emails')

                if day == 66:
                    call_command('send_wave2_no_monitoring_emails')

                if day == 84:
                    call_command('send_wave3_survey_emails')

                if day == 94:
                    call_command('send_wave3_monitoring_emails')
                    participant.wave3_code_entered = True
                    participant.wave3_code_entry_date = current_date
                    participant.save()
                    participant.send_wave3_code_entry_email()
                    self.stdout.write("Wave 3 code entered")

                if day == 102:
                    call_command('send_study_end_emails')

                if day == 103:
                    call_command('send_wave3_missing_code_emails')

                if day == 111:
                    self.stdout.write("Day 112: Use admin panel to export data")

                time.sleep(0.1 / speed)  # Speed-adjusted sleep time
