from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.core import mail
from datetime import timedelta
from testpas.models import Participant
from testpas.forms import CodeEntryForm

class Wave1CodeTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        # Create a participant
        self.participant = Participant.objects.create(
            user=self.user,
            enrollment_date=timezone.now().date() - timedelta(days=11)  # Day 11
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_code_entry_form(self):
        """Test the code entry form validation"""
        form = CodeEntryForm(data={'code': 'wavepa'})
        self.assertTrue(form.is_valid())

        form = CodeEntryForm(data={'code': 'wrongcode'})
        self.assertTrue(form.is_valid())  # Form should be valid as it just checks for input

    def test_correct_code_entry(self):
        """Test entering the correct code"""
        response = self.client.post('/enter-code/', {'code': 'wavepa'})
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        
        # Check that participant's code entry was recorded
        self.participant.refresh_from_db()
        self.assertTrue(self.participant.code_entered)
        self.assertIsNotNone(self.participant.code_entry_date)
        
        # Check that success email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Successful', mail.outbox[0].subject)

    def test_incorrect_code_entry(self):
        """Test entering an incorrect code"""
        response = self.client.post('/enter-code/', {'code': 'wrongcode'})
        self.assertEqual(response.status_code, 200)  # Should stay on same page
        self.assertContains(response, 'Incorrect code')
        
        # Check that participant's code entry was not recorded
        self.participant.refresh_from_db()
        self.assertFalse(self.participant.code_entered)
        self.assertIsNone(self.participant.code_entry_date)
        
        # Check that no email was sent
        self.assertEqual(len(mail.outbox), 0)

    def test_code_entry_time_window(self):
        """Test code entry time window restrictions"""
        # Test before Day 11
        self.participant.enrollment_date = timezone.now().date() - timedelta(days=9)
        self.participant.save()
        response = self.client.get('/enter-code/')
        self.assertEqual(response.status_code, 302)  # Should redirect to failure page

        # Test on Day 11
        self.participant.enrollment_date = timezone.now().date() - timedelta(days=10)
        self.participant.save()
        response = self.client.get('/enter-code/')
        self.assertEqual(response.status_code, 200)  # Should show code entry page

        # Test on Day 20
        self.participant.enrollment_date = timezone.now().date() - timedelta(days=19)
        self.participant.save()
        response = self.client.get('/enter-code/')
        self.assertEqual(response.status_code, 200)  # Should show code entry page

        # Test after Day 20
        self.participant.enrollment_date = timezone.now().date() - timedelta(days=21)
        self.participant.save()
        response = self.client.get('/enter-code/')
        self.assertEqual(response.status_code, 302)  # Should redirect to failure page

    def test_day21_email_notification(self):
        """Test automatic email notification on Day 21"""
        # Set enrollment date to 20 days ago
        self.participant.enrollment_date = timezone.now().date() - timedelta(days=20)
        self.participant.save()
        
        # Run the check_code_entries command
        from django.core.management import call_command
        call_command('check_codes')
        
        # Check that failure email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Deadline Passed', mail.outbox[0].subject)