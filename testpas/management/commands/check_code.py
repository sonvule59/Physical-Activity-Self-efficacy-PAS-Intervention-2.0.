from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from testpas.models import Participant
from datetime import timedelta

class Command(BaseCommand):
    help = 'Checks for participants who didn\'t enter the code by Day 20 and sends them an email on Day 21'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        participants = Participant.objects.filter(
            enrollment_date=today - timedelta(days=20),
            code_entered=False
        )

        for participant in participants:
            subject = "Missing Code Entry (Wave 1)"
            message = f"""
            Hi {participant.user.username},

            You missed the code entry (i.e., no $35 worth of Amazon electronic gift cards). However, you will still have more tasks in the future. We will contact you via email, so please regularly check your inbox.

            If you need any assistance or have any questions at any time, please contact Seungmin (“Seung”) Lee (Principal Investigator) at seunglee@iastate.edu or 517-898-0020.

            Sincerely,

            The Obesity and Physical Activity Research Team
            """

            send_mail(
                subject,
                message,
                'email@gmail.com',
                [participant.user.email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully sent email to {participant.user.email}'))
    # def handle(self, *args, **options):
    #     check_code_entries()