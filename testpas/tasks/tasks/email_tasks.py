from celery import shared_task
from django.core.mail import send_mail
from django.core.management import call_command
from django.apps import apps  # Import apps to use get_model

@shared_task
def send_scheduled_email_task(participant_id):
    ParticipantEntry = apps.get_model('testpas', 'ParticipantEntry')
    EmailContent = apps.get_model('testpas', 'EmailContent')
    
    try:
        entry = ParticipantEntry.objects.get(participant_id=participant_id)
        email_content = EmailContent.objects.latest('id')

        subject = "Survey by Today & Return Monitor (Wave 1)"
        body = f"""
        Hi {entry.participant_id},

        The timeline for wearing the physical activity monitor is complete for this wave.

        Your next two tasks are listed below:

        1. Please complete a short survey. This task must be done by today and should take approximately 10 minutes to complete.
        • Please click the following link to complete the task: [updated link by researchers]

        2. Please return the monitor. Within a couple of days, research members will contact you to arrange the return.

        If you need any assistance or have any questions at any time, please contact Seungmin (“Seung”) Lee (Principal Investigator) at seunglee@iastate.edu or 517-898-0020.

        Sincerely,

        The Obesity and Physical Activity Research Team
        """

        send_mail(
            subject,
            body,
            'from@example.com',
            [entry.email, 'vuleson59@gmail.com']
        )
        
    except ParticipantEntry.DoesNotExist:
        print(f"Participant with ID {participant_id} does not exist.")
    except EmailContent.DoesNotExist:
        print("Email content is not set.")

@shared_task
def run_randomization():
    call_command('randomize_participants')

# def schedule_email(participant_entry):
#     from datetime import timedelta
#     send_date = participant_entry.entry_date + timedelta(days=0)
#     send_date = send_date.replace(hour=0, minute=0, second=10, microsecond=0)
#     send_scheduled_email_task.apply_async((participant_entry.participant_id,), eta=send_date)