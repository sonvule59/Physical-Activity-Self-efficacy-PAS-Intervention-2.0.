# test_timeline.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpas.settings')  # Replace 'PAS_Project.settings' with your project's settings module
django.setup()
from django.core.management import call_command
from django.contrib.auth.models import User
from django.utils import timezone
from freezegun import freeze_time
from testpas.models import Participant, UserSurveyProgress, Survey, EmailTemplate
import time


from testpas.models import EmailTemplate
def setup_participant():
    if User.objects.filter(username='testuser_sonvu1').exists():
        User.objects.filter(username='testuser_sonvu1').delete()
        print("Deleted existing 'testuser_sonvu' to avoid UNIQUE constraint error.")
    if Participant.objects.filter(participant_id='P001').exists():
        Participant.objects.filter(participant_id='P001').delete()
        print("Deleted existing participant 'P001' to avoid UNIQUE constraint error.")
    user = User.objects.create_user(username='testuser_sonvu1', email='vuleson59@gmail.com', password='testpass')
    survey = Survey.objects.create(title="Eligibility Survey", description="Test survey")
    participant = Participant.objects.create(
        user=user,
        email=user.email,
        phone_number='1234567890',
        enrollment_date=timezone.datetime(2025, 4, 3).date(),
        participant_id='P001',
        code_entered=False,
        wave3_code_entered=False,
        wave3_code_entry_date=None,
        group_assigned=False,
        intervention_start_date=None,
        intervention_end_date=None,
        confirmation_token='testtoken',
        # email_status=None,
        email_send_date=None
    )
    UserSurveyProgress.objects.create(
        user=user,
        survey=survey,
        eligible=True,
        consent_given=True,
        day_1=timezone.datetime(2025, 4, 3).date()
    )
    # Response.objects.create(user=user, survey=survey, question="Age", answer="30")
    # Response.objects.create(user=user, survey=survey, question="Activity Level", answer="Moderate")
    return participant

def run_compressed_timeline():
    participant = setup_participant()
    base_date = participant.enrollment_date
    print(f"Starting simulation at {base_date}")

    events = {
        10: "Day 11 - Wave 1 code entry available",
        20: "Day 21 - Check Wave 1 code entry",
        28: "Day 29 - Randomization",
        56: "Day 57 - Wave 2 survey ready",
        66: "Day 67 - No Wave 2 monitoring",
        84: "Day 85 - Wave 3 survey ready",
        94: "Day 95 - Wave 3 monitoring ready",
        103: "Day 104 - Check Wave 3 code entry",
        111: "Day 112 - Data export"
    }

    for day in range(112):
        with freeze_time(base_date + timezone.timedelta(minutes=day)):
            current_date = timezone.now().date()
            print(f"Simulated Date: {current_date} (Minute {day})")

            if day in events:
                print(f"Event: {events[day]}")

            if day == 10:  # Wave 1 code entry (Info 11)
                participant.code_entered = True
                participant.code_entry_date = current_date
                participant.save()
                participant.send_code_entry_email()  # Info 12
                print("Wave 1 code entered")

            if day == 18:  # Info 13
                call_command('send_wave1_survey_emails')

            if day == 20:  # Info 14
                call_command('send_missing_code_emails')

            if day == 28:  # Info 15
                call_command('randomize_participants')

            if day == 56:  # Info 18
                call_command('send_wave2_survey_emails')

            if day == 66:  # Info 19
                call_command('send_wave2_no_monitoring_emails')

            if day == 84:  # Info 20
                call_command('send_wave3_survey_emails')

            if day == 94:  # Wave 3 code entry (Info 22)
                call_command('send_wave3_monitoring_emails')  # Info 21
                participant.wave3_code_entered = True
                participant.wave3_code_entry_date = current_date
                participant.save()
                participant.send_wave3_code_entry_email()  # Info 23
                print("Wave 3 code entered")

            if day == 102:  # Info 24
                call_command('send_study_end_emails')

            if day == 103:  # Info 25
                call_command('send_wave3_missing_code_emails')

            if day == 111:  # Info 26
                print("Day 112: Use admin panel to export data (Info 26)")

            time.sleep(0.1)  # 112 seconds total; use 60 for 112 minutes
            # time.sleep(60)  # Simulate a minute passing
if __name__ == "__main__":
    run_compressed_timeline()