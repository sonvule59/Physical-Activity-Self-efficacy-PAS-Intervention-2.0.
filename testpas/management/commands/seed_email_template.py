# testpas/management/commands/seed_email_templates.py
from django.core.management.base import BaseCommand
from testpas.models import EmailTemplate

class Command(BaseCommand):
    help = 'Seed initial email templates'

    def handle(self, *args, **kwargs):
        EmailTemplate.objects.get_or_create(
            name='account_confirmation',
            defaults={
                'subject': 'Confirm to Activate Your Account',
                'body': 'Hi {participant_id},\n\nPlease click the following link to confirm your registration: {confirmation_link}\n\nSincerely,\nThe Obesity and Physical Activity Research Team'
            }
        )
        self.stdout.write(self.style.SUCCESS('Email templates seeded successfully'))