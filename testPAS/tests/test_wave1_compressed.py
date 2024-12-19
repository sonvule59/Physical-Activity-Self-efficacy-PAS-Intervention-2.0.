# testpas/tests/test_wave1_compressed.py

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.core import mail
from datetime import datetime, timedelta
from freezegun import freeze_time
from testpas.models import Participant
from django.urls import reverse
import pytz

class Wave1CompressedTimelineTest(TestCase):
    def setUp(self):
        # Set up reference time (December 19, 2024, 17:36:36 UTC)
        self.reference_time = datetime(2024, 12, 19, 17, 36, 36, tzinfo=pytz.UTC)
        
        # Create test user
        self.user = User.objects.create_user(
            username='sonvule59',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='sonvule59', password='testpass123')

    def test_compressed_timeline(self):
        """Test entire Wave 1 timeline in compressed time"""
        
        # Day 1: Enrollment
        with freeze_time(self.reference_time):
            participant = Participant.objects.create(
                user=self.user,
                enrollment_date=timezone.now().date()
            )
            
            response = self.client.get(reverse('dashboard'))
            self.assertContains(response, "Wave 1 Code Entry Period Starting Soon")
            print(f"\nDay 1 ({timezone.now()}): Enrollment completed")

        # Day 10: Pre-window notification
        with freeze_time(self.reference_time + timedelta(days=9)):
            response = self.client.get(reverse('dashboard'))
            self.assertContains(response, "Starting Soon")
            mail.outbox = []
            self.client.get(reverse('check_daily_emails'))
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('Starting Tomorrow', mail.outbox[0].subject)
            print(f"Day 10 ({timezone.now()}): Pre-window notification sent")

        # Day 11: Window Opens
        with freeze_time(self.reference_time + timedelta(days=10)):
            response = self.client.get(reverse('dashboard'))
            self.assertContains(response, "Code Entry Period Active")
            
            # Test incorrect code
            response = self.client.post(reverse('enter_code'), {'code': 'wrongcode'})
            self.assertContains(response, "Incorrect code")
            print(f"Day 11 ({timezone.now()}): Code entry window opened")

        # Day 15: Enter Code
        with freeze_time(self.reference_time + timedelta(days=14)):
            mail.outbox = []
            response = self.client.post(reverse('enter_code'), {'code': 'wavepa'})
            self.assertRedirects(response, reverse('code_success'))
            
            # Verify code was recorded
            participant.refresh_from_db()
            self.assertTrue(participant.code_entered)
            self.assertEqual(participant.code_entry_date, timezone.now().date())
            
            # Check confirmation email
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('Code Entry Confirmation', mail.outbox[0].subject)
            print(f"Day 15 ({timezone.now()}): Code entered successfully")

        # Day 23 (8 days after code entry): Survey Email
        survey_date = self.reference_time + timedelta(days=22)
        survey_time = survey_date.replace(hour=7, minute=0, second=0)  # 7 AM CT
        with freeze_time(survey_time):
            mail.outbox = []
            self.client.get(reverse('check_daily_emails'))
            
            # Verify survey email
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            self.assertEqual(email.subject, 'Survey by Today & Return Monitor (Wave 1)')
            self.assertIn('seunglee@iastate.edu', email.cc)
            print(f"Day 23 ({timezone.now()}): Survey email sent")

        # Day 21: Window Closes
        with freeze_time(self.reference_time + timedelta(days=20)):
            response = self.client.get(reverse('dashboard'))
            self.assertNotContains(response, "Code Entry Period Active")
            print(f"Day 21 ({timezone.now()}): Window closed")

    def test_missed_deadline(self):
        """Test scenario where participant misses the deadline"""
        
        # Create participant
        with freeze_time(self.reference_time):
            participant = Participant.objects.create(
                user=self.user,
                enrollment_date=timezone.now().date()
            )

        # Jump to Day 21 without entering code
        with freeze_time(self.reference_time + timedelta(days=20)):
            mail.outbox = []
            self.client.get(reverse('check_daily_emails'))
            
            # Verify missed deadline email
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('Missed Code Entry', mail.outbox[0].subject)
            print(f"\nMissed Deadline Test ({timezone.now()}): Email sent")

if __name__ == '__main__':
    print("Running Wave 1 compressed timeline tests...")