from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from testpas.models import Participant
from datetime import datetime, timedelta
from freezegun import freeze_time
import time
import pytz

class Command(BaseCommand):
    help = 'Simulate entire Wave 1 timeline in compressed time (about 2 minutes total)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delay',
            type=int,
            default=10,
            help='Seconds to wait between each day (default: 10)'
        )

    def handle(self, *args, **kwargs):
        delay = kwargs['delay']
        start_date = datetime(2024, 12, 19, 17, 34, 54, tzinfo=pytz.UTC)  # Your current date

        self.stdout.write(self.style.SUCCESS(f'\nStarting Wave 1 Timeline Simulation'))
        self.stdout.write(f'Current time: {timezone.now()}')
        self.stdout.write(f'Simulating each day with {delay} second delay\n')

        # Get or create test user
        user = User.objects.get(username='sonvu41')
        
        # Create participant
        participant, created = Participant.objects.get_or_create(
            user=user,
            defaults={'enrollment_date': start_date.date()}
        )

        # Day 1: Enrollment
        with freeze_time(start_date):
            self.stdout.write(self.style.SUCCESS(f'\nDAY 1 - {timezone.now()}'))
            self.stdout.write('Enrolling participant...')
            participant.enrollment_date = timezone.now().date()
            participant.save()
            
            send_mail(
                'Welcome to Wave 1',
                f'Dear {user.username},\n\nYou have been enrolled in Wave 1.',
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )
            time.sleep(delay)

        # Simulate Days 2-10 (Pre-window period)
        self.stdout.write(self.style.SUCCESS('\nDays 2-10: Pre-window period'))
        simulated_date = start_date + timedelta(days=9)
        with freeze_time(simulated_date):
            self.stdout.write(f'Day 10 - {timezone.now()}')
            send_mail(
                'Code Entry Window Starting Tomorrow',
                'Your code entry window begins tomorrow.',
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )
            time.sleep(delay)

        # Day 11: Code Entry Window Opens
        simulated_date = start_date + timedelta(days=10)
        with freeze_time(simulated_date):
            self.stdout.write(self.style.SUCCESS(f'\nDAY 11 - {timezone.now()}'))
            self.stdout.write('Code entry window is now open')
            send_mail(
                'Code Entry Window Now Open',
                'You can now enter your code: wavepa',
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )
            time.sleep(delay)

        # Day 15: Code Entry
        simulated_date = start_date + timedelta(days=14)
        with freeze_time(simulated_date):
            self.stdout.write(self.style.SUCCESS(f'\nDAY 15 - {timezone.now()}'))
            self.stdout.write('Simulating code entry...')
            
            # Simulate successful code entry
            participant.code_entered = True
            participant.code_entry_date = timezone.now().date()
            participant.save()
            
            # Send confirmation email (Information 12)
            send_mail(
                'Code Entry Confirmation',
                'Your code has been successfully entered.',
                'noreply@example.com',
                [user.email],
                # cc=['seunglee@iastate.edu'],
                fail_silently=False,
            )
            time.sleep(delay)

        # Day 23 (8 days after code entry): Survey Email
        simulated_date = start_date + timedelta(days=22)
        survey_time = simulated_date.replace(hour=7, minute=0, second=0)  # 7 AM CT
        with freeze_time(survey_time):
            self.stdout.write(self.style.SUCCESS(f'\nDAY 23 - {timezone.now()}'))
            self.stdout.write('Sending survey email...')
            
            # Send survey email (Information 13)
            send_mail(
                'Survey by Today & Return Monitor (Wave 1)',
                'Please complete the survey and return the monitor.',
                'noreply@example.com',
                [user.email],
                # cc=['seunglee@iastate.edu'],
                fail_silently=False,
            )
            time.sleep(delay)

        # Day 21: End of Window
        simulated_date = start_date + timedelta(days=20)
        with freeze_time(simulated_date):
            self.stdout.write(self.style.SUCCESS(f'\nDAY 21 - {timezone.now()}'))
            self.stdout.write('Code entry window is now closed')
            send_mail(
                'Code Entry Window Closed',
                'The code entry window is now closed.',
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )

        self.stdout.write(self.style.SUCCESS('\nSimulation Complete!'))
        self.stdout.write('Timeline Summary:')
        self.stdout.write(f'Enrollment Date: {participant.enrollment_date}')
        self.stdout.write(f'Code Entry Date: {participant.code_entry_date}')
        self.stdout.write(f'Code Entered Successfully: {participant.code_entered}')
