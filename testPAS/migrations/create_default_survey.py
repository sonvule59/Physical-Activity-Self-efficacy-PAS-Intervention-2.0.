from django.db import migrations
from django.utils import timezone

def create_default_survey(apps, schema_editor):
    Survey = apps.get_model('testpas', 'Survey')
    Question = apps.get_model('testpas', 'Question')
    
    # Create the initial survey
    survey = Survey.objects.create(
        title="Initial Interest Survey",
        description="Please complete this survey to help us understand your interest in the study.",
        created_at=timezone.now()
    )

    # Add some initial questions
    questions = [
        "Are you interested in participating in physical activity research?",
        "How often do you currently exercise?",
        "What are your fitness goals?"
    ]
    
    for question_text in questions:
        Question.objects.create(
            survey=survey,
            question_text=question_text,
            created_at=timezone.now()
        )

def remove_default_survey(apps, schema_editor):
    Survey = apps.get_model('testpas', 'Survey')
    Survey.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('testPAS', '0001_initial'),  # Replace with your last migration
    ]

    operations = [
        migrations.RunPython(create_default_survey, remove_default_survey),
    ]