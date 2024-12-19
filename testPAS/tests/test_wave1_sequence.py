from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.core import mail
from datetime import timedelta
from testpas.models import Participant
from django.urls import reverse
from freezegun import freeze_time  # You'll need to install this: pip install freezegun

class Wave1SequenceTestCase(TestCase):
    def setUp(self):
        # Create test user and participant
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='vuleson59@gmail.com'
        )
        # Set enrollment date to January 1st, 2025
        enrollment_date = timezone.datetime(2025, 1, 1).date()
        self.participant = Participant.objects.create(
            user=self.user,
            enrollment_date=enrollment_date
        )
        self.client.login(username='testuser', password='testpass123')

    def test_complete_registration_sequence(self):
        """Test the complete registration and questionnaire sequence"""
        # Registration data
        registration_data = {
            'registration-code': 'wavepa',
            'user-id': 'newuser',
            'password': 'newpass123',
            'password-confirmation': 'newpass123',
            'email': 'new@example.com'
        }
        
        # Step 1: Register account
        response = self.client.post('/create-account/', registration_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)  # Verify registration email sent

        # Step 2: Answer questionnaire (example data)
        questionnaire_data = {
            'age': '30',
            'height': '70',  # inches
            'weight': '200',  # lbs
            'has_device': 'yes',
            'not_enroll_other': 'yes',
            'comply_monitoring': 'yes',
            'respond_contacts': 'yes'
        }
        response = self.client.post('/questionnaire/', questionnaire_data)
        self.assertEqual(response.status_code, 302)  # Should redirect to next step

    @freeze_time("2025-01-10")  # Day 10 (before window)
    def test_before_time_window(self):
        """Test accessing code entry before Day 11"""
        response = self.client.get('/enter-code/')
        self.assertEqual(response.status_code, 302)  # Should redirect to failure page
        self.assertRedirects(response, '/code-failure/')

    @freeze_time("2025-01-11")  # Day 11 (start of window)
    def test_start_of_time_window(self):
        """Test code entry on first day of window (Day 11)"""
        response = self.client.get('/enter-code/')
        self.assertEqual(response.status_code, 200)  # Should show code entry page
        self.assertTemplateUsed(response, 'enter_code.html')

    @freeze_time("2025-01-15")  # Day 15 (during window)
    def test_correct_code_entry(self):
        """Test entering correct code during window"""
        response = self.client.post('/enter-code/', {'code': 'WAVEPA'})  # Test case-insensitive
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/code-success/')
        
        # Verify success email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Wave 1 Physical Activity Code Entry Successful', mail.outbox[0].subject)

    @freeze_time("2025-01-15")  # Day 15 (during window)
    def test_incorrect_code_entry(self):
        """Test entering incorrect code during window"""
        response = self.client.post('/enter-code/', {'code': 'wrongcode'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'enter_code.html')
        self.assertContains(response, 'Incorrect code')

    @freeze_time("2025-01-20")  # Day 20 (last day of window)
    def test_last_day_of_window(self):
        """Test code entry on last day of window"""
        response = self.client.get('/enter-code/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'enter_code.html')

    @freeze_time("2025-01-21")  # Day 21 (after window)
    def test_after_time_window(self):
        """Test accessing code entry after Day 20"""
        # Test that code entry page is no longer accessible
        response = self.client.get('/enter-code/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/code-failure/')

    @freeze_time("2025-01-21")  # Day 21
    def test_day21_notification(self):
        """Test that email is sent on Day 21 if code wasn't entered"""
        # Clear any existing emails
        mail.outbox = []
        
        # Run the check_code_entries command
        from django.core.management import call_command
        call_command('check_codes')
        
        # Verify failure email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Deadline Passed', mail.outbox[0].subject)

    def test_dashboard_visibility(self):
        """Test that code entry information is visible only during the window"""
        # Test before window (Day 10)
        with freeze_time("2025-01-10"):
            response = self.client.get('/dashboard/')
            self.assertNotContains(response, 'Enter Wave 1 Code')

        # Test during window (Day 15)
        with freeze_time("2025-01-15"):
            response = self.client.get('/dashboard/')
            self.assertContains(response, 'Enter Wave 1 Code')

        # Test after window (Day 21)
        with freeze_time("2025-01-21"):
            response = self.client.get('/dashboard/')
            self.assertNotContains(response, 'Enter Wave 1 Code')