# testpas/management/commands/seed_eligibility_survey.py
from django.core.management.base import BaseCommand
from testpas.models import Survey, Question
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds eligibility survey and questions'

    def handle(self, *args, **kwargs):
        #  Create eligibility survey
        survey, created = Survey.objects.get_or_create(
            title="Eligibility Criteria",
            defaults={"description": "Survey to determine participant eligibility"}
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created eligibility survey"))

        # Create eligibility questions
        questions = [
            {
                "question_text": (
                    "Will you have access to a technological device (e.g., computer, smart phone) "
                    "that can access the online intervention via a web browser throughout this study?"
                )
            },
            {
                "question_text": (
                    "Do you agree not to enroll in another research-based intervention program "
                    "promoting physical activity while participating in this study?"
                )
            },
            {
                "question_text": (
                    "Do you agree to comply with instructions for physical activity monitoring in this study?"
                )
            },
            {
                "question_text": (
                    "Do you agree to respond to our contacts?"
                )
            },
        ]

        for idx, q in enumerate(questions, start=1):
            Question.objects.get_or_create(
                survey=survey,
                question_text=q["question_text"],
                defaults={"created_at": timezone.now()}
            )
            self.stdout.write(self.style.SUCCESS(f"Created question {idx}"))

        self.stdout.write(self.style.SUCCESS("Eligibility survey seeding complete"))