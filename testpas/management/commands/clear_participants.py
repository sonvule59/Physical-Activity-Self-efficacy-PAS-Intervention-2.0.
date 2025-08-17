from django.core.management.base import BaseCommand
from testpas.models import Participant, UserSurveyProgress, SurveyProgress, Response, Token, Content
from django.contrib.auth.models import User
from django.db import transaction

## In the terminal, run the following commands to clear the participants and related data
## python manage.py clear_participants --confirm --keep-users if you want to keep the users and only delete the participant data
## python manage.py clear_participants --confirm if you want to delete all data

## If you want to keep the users and only delete the participant data, run the following command
## python manage.py clear_participants --confirm --keep-users

## If you want to delete all data, run the following command
## python manage.py clear_participants --confirm

class Command(BaseCommand):
    help = 'Clear all participants and related data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data'
        )
        parser.add_argument(
            '--keep-users',
            action='store_true',
            help='Keep User accounts but delete participant data'
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    "This will delete ALL participants and related data!\n"
                    "Run with --confirm to proceed.\n"
                    "Use --keep-users to keep User accounts but delete participant data."
                )
            )
            return

        with transaction.atomic():
            # Count records before deletion
            participant_count = Participant.objects.count()
            user_progress_count = UserSurveyProgress.objects.count()
            survey_progress_count = SurveyProgress.objects.count()
            response_count = Response.objects.count()
            token_count = Token.objects.count()
            user_count = User.objects.count()

            self.stdout.write(f"Found {participant_count} participants")
            self.stdout.write(f"Found {user_progress_count} user progress records")
            self.stdout.write(f"Found {survey_progress_count} survey progress records")
            self.stdout.write(f"Found {response_count} responses")
            self.stdout.write(f"Found {token_count} tokens")
            self.stdout.write(f"Found {user_count} users")

            # Delete participant-related data
            Participant.objects.all().delete()
            UserSurveyProgress.objects.all().delete()
            SurveyProgress.objects.all().delete()
            Response.objects.all().delete()
            Token.objects.all().delete()

            if not options['keep_users']:
                # Delete all users (except superuser)
                User.objects.filter(is_superuser=False).delete()
                self.stdout.write("Deleted all non-superuser accounts")
            else:
                self.stdout.write("Kept User accounts, only deleted participant data")

            # Keep Content records (they're for website content)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully cleared all participant data!\n"
                    f"Deleted: {participant_count} participants, {user_progress_count} progress records, "
                    f"{survey_progress_count} survey progress, {response_count} responses, {token_count} tokens"
                )
            ) 