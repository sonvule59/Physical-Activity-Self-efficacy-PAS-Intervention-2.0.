from django.core.management.base import BaseCommand
from testpas.models import Participant
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Command(BaseCommand):
    help = 'Add test participants to the database'

    def add_arguments(self, parser):
        parser.add_argument('num_participants', type=int, help='Number of participants to add')

    def handle(self, *args, **kwargs):
        num_participants = kwargs['num_participants']
        fixed_email = "holden.smith.ia@gmail.com"
        existing_count = Participant.objects.count()

        test_user, _ = User.objects.get_or_create(
            username='testuser',
            defaults={'email': fixed_email}
        )
        existing_count = Participant.objects.count()

        for i in range(num_participants):
            participant_id = f"P{existing_count + i + 1:03d}"  # e.g., P001, P002
            # email = f"participant{existing_count + i + 1}@example.com"
            participant = Participant(
                user = test_user,
                participant_id=participant_id,
                email=fixed_email,
                group_assigned=False,  # Ensure they’re ready for randomization
                confirmation_token=str(uuid.uuid4()),  # Required: unique token
            )
            participant.save()
            self.stdout.write(self.style.SUCCESS(f"Added participant: {participant_id}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully added {num_participants} participants."))