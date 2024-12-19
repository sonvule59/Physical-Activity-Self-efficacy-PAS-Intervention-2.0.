from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.core import mail
from datetime import datetime, timedelta
from freezegun import freeze_time
from testpas.models import Participant
from django.urls import reverse
import pytz

class Wave1TimelineTestCase(TestCase):
    def setUp(self):
        # Set up current date and time (December 19, 2024, 17:30:54 UTC)
        self.current_datetime = datetime(2024, 12, 19, 17, 30, 54, tzinfo=pytz.UTC)
        
        # Create test user with actual username
        self.user = User.objects.create_user(
            username='sonvule59',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='sonvule59', password='testpass123')

    def test_wave1_timeline(self):
        """Test Wave 1 timeline starting from current date"""
        
        # Start by freezing time to current moment
        with freeze_time(self.current_datetime):
            print(f"\nCurrent date-time: {timezone.now()}")
            
            # Calculate enrollment date (11 days ago from current date)
            enrollment_date = timezone.now().date() - timedelta(days=11)
            
            # Create participant with enrollment date 11 days ago
            participant = Participant.objects.create(
                user=self.user,
                enrollment_date=enrollment_date
            )
            
            print(f"Enrollment date: {enrollment_date}")
            print(f"Days since enrollment: {(timezone.now().date() - enrollment_date).days}")
            
            # Verify we're in the active window
            response = self.client.get(reverse('dashboard'))
            self.assertContains(response, "Code Entry Period Active")
            print("Verified: Currently in active code entry window")

            # Test incorrect code
            response = self.client.post(reverse('enter_code'), {'code': 'wrongcode'})
            self.assertContains(response, "Incorrect code")
            print("Tested: Incorrect code rejected")

            # Test correct code
            mail.outbox = []
            response = self.client.post(reverse('enter_code'), {'code': 'wavepa'})
            self.assertRedirects(response, reverse('code_success'))
            
            # Verify immediate email sent (Information 12)
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('Code Entry Confirmation', mail.outbox[0].subject)
            print("Tested: Correct code accepted and confirmation email sent")

        # Test future dates
        # Day 20 (Last day to enter code - December 28, 2024)
        with freeze_time("2024-12-28 23:59:59"):
            response = self.client.get(reverse('dashboard'))
            self.assertContains(response, "Code Entry Period Active")
            print("\nTested: Last day to enter code (Dec 28)")

        # Day 21 (Code entry should disappear - December 29, 2024)
        with freeze_time("2024-12-29 00:00:00"):
            response = self.client.get(reverse('dashboard'))
            self.assertNotContains(response, "Code Entry Period Active")
            print("Tested: Code entry form removed (Dec 29)")

        # Day 27 (8 days after code entry - December 27, 2024 7:00 AM CT)
        with freeze_time("2024-12-27 07:00:00-06:00"):
            mail.outbox = []
            self.client.get(reverse('check_daily_emails'))
            
            # Verify survey email
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            self.assertEqual(email.subject, 'Survey by Today & Return Monitor (Wave 1)')
            self.assertIn('seunglee@iastate.edu', email.cc)
            print("Tested: Survey email sent 8 days after code entry")

    def test_missed_deadline_scenario(self):
        """Test what happens if participant doesn't enter code by December 28"""
        
        with freeze_time(self.current_datetime):
            # Create participant with enrollment date 11 days ago
            enrollment_date = timezone.now().date() - timedelta(days=11)
            participant = Participant.objects.create(
                user=self.user,
                enrollment_date=enrollment_date
            )

        # Jump to December 29 (Day 21) without entering code
        with freeze_time("2024-12-29 00:00:00"):
            mail.outbox = []
            self.client.get(reverse('check_daily_emails'))
            
            # Verify missed deadline email
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            self.assertIn('Missed Code Entry', email.subject)
            print("\nTested: Missed deadline email sent")

    def test_time_window_calculations(self):
        """Test time window calculations based on December 19 enrollment"""
        
        with freeze_time(self.current_datetime):
            participant = Participant.objects.create(
                user=self.user,
                enrollment_date=timezone.now().date()
            )
            
            # Calculate important dates
            day_11 = participant.enrollment_date + timedelta(days=10)  # December 29
            day_20 = participant.enrollment_date + timedelta(days=19)  # January 7
            day_21 = participant.enrollment_date + timedelta(days=20)  # January 8
            
            print(f"\nEnrollment date: {participant.enrollment_date}")
            print(f"Code entry window starts: {day_11}")
            print(f"Code entry window ends: {day_20}")
            print(f"Information disappears: {day_21}")

if __name__ == '__main__':
    print("Running Wave 1 timeline tests from December 19, 2024...")