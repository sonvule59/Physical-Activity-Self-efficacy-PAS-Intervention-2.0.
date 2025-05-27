from datetime import timedelta
from celery import shared_task
from django.core.mail import send_mail
from django.core.management import call_command
from django.apps import apps  # Import apps to use get_model
from testpas import settings
from django.utils import timezone
import random
from testpas.models import Participant
import logging
logger = logging.getLogger(__name__)
@shared_task
def send_scheduled_emails():
    now = timezone.now()
    logger.info(f"Running send_scheduled_emails at {now}")
    participants = Participant.objects.filter(is_confirmed=True, engagement_tracked=True)
    logger.info(f"Found {participants.count()} eligible participants")
    for participant in participants:
        start_date = participant.enrollment_date
        if not start_date:
            logger.error(f"Participant {participant.participant_id} has no enrollment_date, skipping")
            continue
        try:
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(start_date, timezone.datetime.min.time()),
                timezone.get_default_timezone()
            )
            if settings.TEST_MODE:
                elapsed = (now - start_datetime).total_seconds() / settings.TEST_TIME_SCALE
                if elapsed > 365:  # Cap at 1 year to catch errors
                    logger.error(f"Participant {participant.participant_id} has unrealistic elapsed time {elapsed:.2f} days, skipping")
                    continue
            else:
                elapsed = (now.date() - start_date).days
            logger.info(f"Participant {participant.participant_id}: elapsed={elapsed:.2f} days, code_entry_date={participant.code_entry_date}")

            # Information 10: Day 11
            if elapsed >= 11 and elapsed < 21 and not participant.code_entry_date and participant.email_status != 'sent_wave1_monitor':
                logger.info(f"Attempting to send wave1_monitor_ready to {participant.email}")
                participant.send_email('wave1_monitor_ready', mark_as='sent_wave1_monitor')
            # Information 14: Day 21
            elif elapsed >= 21 and not participant.code_entered and participant.email_status != 'sent_wave1_missing':
                logger.info(f"Attempting to send wave1_missing_code to {participant.email}")
                participant.send_email('wave1_missing_code', mark_as='sent_wave1_missing')
            # Information 15-17: Day 29
            elif 29 <= elapsed < 57 and not participant.group_assigned and participant.email_status != 'sent_intervention':
                participant.group = random.randint(0, 1)
                participant.group_assigned = True
                participant.intervention_start_date = now
                participant.save()
                template = 'intervention_access_later' if participant.group == 0 else 'intervention_access_immediate'
                logger.info(f"Attempting to send {template} to {participant.email}")
                participant.send_email(template, extra_context={'login_link': settings.BASE_URL + '/login/'}, mark_as='sent_intervention')
            # Information 18: Day 57
            elif 29 <= elapsed < 57 and participant.email_status != 'sent_wave2_survey':
                logger.info(f"Attempting to send wave2_survey_ready to {participant.email}")
                participant.send_email('wave2_survey_ready', mark_as='sent_wave2_survey')
            # Information 19: Day 67
            elif 67 <= elapsed < 85 and participant.email_status != 'sent_wave2_no_monitoring':
                logger.info(f"Attempting to send wave2_no_monitoring to {participant.email}")
                participant.send_email('wave2_no_monitoring', mark_as='sent_wave2_no_monitoring')
            # Information 20: Day 85
            elif 85 <= elapsed < 95 and participant.email_status != 'sent_wave3_survey':
                logger.info(f"Attempting to send wave3_survey_ready to {participant.email}")
                participant.send_email('wave3_survey_ready', mark_as='sent_wave3_survey')
            # Information 21: Day 95
            elif 95 <= elapsed < 105 and not participant.wave3_code_entry_date and participant.email_status != 'sent_wave3_monitoring':
                logger.info(f"Attempting to send wave3_monitoring_ready to {participant.email}")
                participant.send_email('wave3_monitoring_ready', mark_as='sent_wave3_monitoring')
            # Information 25: Day 105
            elif 95 <= elapsed < 105 and not participant.wave3_code_entered and participant.email_status != 'sent_wave3_missing':
                logger.info(f"Attempting to send wave3_missing_code to {participant.email}")
                participant.send_email('wave3_missing_code', mark_as='sent_wave3_missing')
            # Information End: Day 112
            elif elapsed >= 112 and participant.email_status != 'sent_study_end':
                logger.info(f"Attempting to send study_end to {participant.email}")
                participant.send_email('study_end', mark_as='sent_study_end')
        except Exception as e:
            logger.error(f"Error processing participant {participant.participant_id}: {e}")
            continue

@shared_task
def send_wave3_code_entry_email(participant_id):
    """Information 23: Physical Activity Monitoring Tomorrow (Wave 3)"""
    try:
        participant = Participant.objects.get(id=participant_id)
        
        # Calculate dates
        code_date = participant.wave3_code_entry_date
        start_date = code_date + timedelta(days=1)
        end_date = code_date + timedelta(days=7)
        
        participant.send_email(
            'wave3_code_entry',
            extra_context={
                'code_date': code_date.strftime('%m/%d/%Y'),
                'start_date': start_date.strftime('%m/%d/%Y'),
                'end_date': end_date.strftime('%m/%d/%Y'),
            }
        )
        logger.info(f"Sent Wave 3 code entry email to {participant.participant_id}")
    except Exception as e:
        logger.error(f"Error sending Wave 3 code entry email: {str(e)}")

@shared_task
def send_specific_email(participant_id, template_name, extra_context=None):
    try:
        participant = Participant.objects.get(id=participant_id)
        logger.info(f"Attempting to send {template_name} to {participant.email}")
        participant.send_email(template_name, extra_context)
        logger.info(f"Sent {template_name} to {participant.email}")
    except Participant.DoesNotExist:
        logger.error(f"Participant {participant_id} not found for {template_name}")
    except Exception as e:
        logger.error(f"Error sending {template_name} for participant {participant_id}: {e}")
# def send_scheduled_emails():
#     now = timezone.now()
#     participants = Participant.objects.filter(is_confirmed=True, engagement_tracked=True)
#     # for participant in Participant.objects.filter(is_confirmed=True, engagement_tracked=True):
#     for participant in participants:
#         # start_date = participant.consent_date or participant.enrollment_date
#         start_date = participant.enrollment_date
#         if not start_date:
#             logger.warning(f"Participant {participant.participant_id} has no consent_date, using enrollment_date")
#             start_date = participant.enrollment_date
#         if not start_date:
#             logger.error(f"Participant {participant.participant_id} has no start_date, skipping")
#             continue
#         if settings.TEST_MODE:
#             elapsed = (now - timezone.datetime.combine(start_date, timezone.datetime.min.time())).total_seconds() / settings.TEST_TIME_SCALE
#         else:
#             elapsed = (now.date() - start_date).days
#         logger.debug(f"Participant {participant.participant_id}: elapsed={elapsed:.2f} days")

#         # Information 9: Handled in consent_form
#         # Information 10: Day 11
#         if elapsed >= 11 and not participant.code_entry_date:
#             participant.send_email('wave1_monitor_ready')
#         # Information 14: Day 21
#         elif elapsed >= 21 and not participant.code_entered:
#             participant.send_missing_code_email()
#         # Information 15-17: Day 29
#         elif elapsed >= 29 and not participant.group_assigned:
#             participant.group = random.randint(0, 1)
#             participant.group_assigned = True
#             participant.intervention_start_date = now
#             participant.save()
#             template = 'intervention_access_later' if participant.group == 0 else 'intervention_access_immediate'
#             participant.send_email(template, {'login_link': settings.BASE_URL + '/login/'})
#         # Information 18: Day 57
#         elif elapsed >= 57:
#             participant.send_wave2_survey_email()
#         # Information 19: Day 67
#         elif elapsed >= 67:
#             participant.send_wave2_no_monitoring_email()
#         # Information 20: Day 85
#         elif elapsed >= 85:
#             participant.send_wave3_survey_email()
#         # Information 21: Day 95
#         elif elapsed >= 95 and not participant.wave3_code_entry_date:
#             participant.send_wave3_monitoring_email()
#         # Information 25: Day 105
#         elif elapsed >= 105 and not participant.wave3_code_entered:
#             participant.send_wave3_missing_code_email()
 
@shared_task
def run_randomization():
    call_command('randomize_participants')

# def schedule_email(participant_entry):
#     from datetime import timedelta
#     send_date = participant_entry.entry_date + timedelta(days=0)
#     send_date = send_date.replace(hour=0, minute=0, second=10, microsecond=0)
#     send_scheduled_email_task.apply_async((participant_entry.participant_id,), eta=send_date)