from datetime import timedelta
from celery import shared_task
from django.core.mail import send_mail
from django.core.management import call_command
from django.apps import apps
from psutil import users  # Import apps to use get_model
# from .views import get_current_time
from testpas import settings
from django.utils import timezone
import random
from testpas.models import Participant, EmailTemplate
import logging

from testpas.views import get_current_time
from .models import User
logger = logging.getLogger(__name__)

from .timeline import get_timeline_day
### Jun 11: Add in run_daily_timeline_checks task among other tasks
@shared_task
def run_daily_timeline_checks():
    for user in User.objects.all():
        daily_timeline_check(user)

def daily_timeline_check(user):
    seconds_per_day = getattr(settings, 'SECONDS_PER_DAY', 86400)
    compressed = getattr(settings, 'TIME_COMPRESSION', False)

    today = get_timeline_day(user, compressed=compressed, seconds_per_day=seconds_per_day)

    if today == 1:
        send_mail(
            "Wave 1 Survey Ready",
            f"Hi {user.username}, do this task...",
            "vuleson59@gmail.com",
            [user.email]
        )
    elif today == 11:
        send_mail(
            "Wave 1 Monitor Ready",
            f"Hi {user.username}, do this task...",
            "vuleson59@gmail.com",
            [user.email]
        )
    elif today == 21 and not user.wave1_code_entered:
        send_mail(
            "Missed Wave 1 Code Entry",
            f"Hi {user.username}, ...",
            "vuleson59@gmail.com",
            [user.email]
        )
    elif today == 29 and user.randomized_group is None:
        user.randomized_group = random.choice([0, 1])
        user.save()
        if user.randomized_group == 0:
            send_mail(
                "Intervention Access Later",
                f"Hi {user.username}, you will receive access after the study ends.",
                "vuleson59@gmail.com",
                [user.email]
            )
        else:
            send_mail(
                "Intervention Access Immediately",
                f"Hi {user.username}, you now have immediate access to the intervention.",
                "vuleson59@gmail.com",
                [user.email]
            )
### END Jun 11: Add in run_daily_timeline_checks task among other tasks
# def get_current_time():
#     global _fake_time
#     if _fake_time is not None:
#         return _fake_time
#     return timezone.now()
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
                participant.send_email('wave1_monitor_ready')
            # Information 14: Day 21
            if elapsed >= 21 and not participant.code_entered and participant.email_status != 'sent_wave1_missing':
                send_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
                if now.hour >= 7:
                    send_time += timedelta(days=1)
                participant.send_email('wave1_missing_code', extra_context={'username': participant.user.username})
                participant.email_status = 'sent_wave1_missing'
                participant.save()
                logger.info(f"Sent wave1_missing_code to {participant.email}")

            # Schedule Information 13 email 8 days after code entry
            if participant.code_entry_date:
                code_entry_datetime = timezone.make_aware(
                    timezone.datetime.combine(participant.code_entry_date, timezone.datetime.min.time()),
                    timezone.get_default_timezone()
                )
                if settings.TEST_MODE:
                    elapsed_code = (now - code_entry_datetime).total_seconds() / settings.TEST_TIME_SCALE
                else:
                    elapsed_code = (now.date() - participant.code_entry_date).days
                if elapsed_code >= 8 and participant.email_status != 'sent_wave1_survey_return':
                    send_wave1_survey_return_email(participant.participant_id)
            # elif 29 <= elapsed < 57 and not participant.group_assigned and participant.email_status != 'sent_intervention':
            #     participant.group = random.randint(0, 1)
            #     participant.group_assigned = True
            #     participant.intervention_start_date = now
            #     participant.save()
            #     template = 'intervention_access_later' if participant.group == 0 else 'intervention_access_immediate'
            #     logger.info(f"Attempting to send {template} to {participant.email}")
            #     participant.send_email(template, extra_context={'login_link': settings.BASE_URL + '/login/'}, mark_as='sent_intervention')
            # # Information 18: Day 57
            # elif 29 <= elapsed < 57 and participant.email_status != 'sent_wave2_survey':
            #     logger.info(f"Attempting to send wave2_survey_ready to {participant.email}")
            #     participant.send_email('wave2_survey_ready', mark_as='sent_wave2_survey')
            # # Information 19: Day 67
            # elif 67 <= elapsed < 85 and participant.email_status != 'sent_wave2_no_monitoring':
            #     logger.info(f"Attempting to send wave2_no_monitoring to {participant.email}")
            #     participant.send_email('wave2_no_monitoring', mark_as='sent_wave2_no_monitoring')
            # # Information 20: Day 85
            # elif 85 <= elapsed < 95 and participant.email_status != 'sent_wave3_survey':
            #     logger.info(f"Attempting to send wave3_survey_ready to {participant.email}")
            #     participant.send_email('wave3_survey_ready', mark_as='sent_wave3_survey')
            # # Information 21: Day 95
            # elif 95 <= elapsed < 105 and not participant.wave3_code_entry_date and participant.email_status != 'sent_wave3_monitoring':
            #     logger.info(f"Attempting to send wave3_monitoring_ready to {participant.email}")
            #     participant.send_email('wave3_monitoring_ready', mark_as='sent_wave3_monitoring')
            # # Information 25: Day 105
            # elif 95 <= elapsed < 105 and not participant.wave3_code_entered and participant.email_status != 'sent_wave3_missing':
            #     logger.info(f"Attempting to send wave3_missing_code to {participant.email}")
            #     participant.send_email('wave3_missing_code', mark_as='sent_wave3_missing')
            # # Information End: Day 112
            # elif elapsed >= 112 and participant.email_status != 'sent_study_end':
            #     logger.info(f"Attempting to send study_end to {participant.email}")
            #     participant.send_email('study_end', mark_as='sent_study_end')
        except Exception as e:
            logger.error(f"Error processing participant {participant.participant_id}: {e}")
            continue
@shared_task
def send_wave1_survey_return_email(participant_id):
    """Information 13: Survey by Today & Return Monitor (Wave 1)"""
    try:
        participant = Participant.objects.get(id=participant_id)
        if participant.email_status == 'sent_wave1_survey_return':
            logger.info(f"Skipping wave1_survey_return for {participant.email}: already sent")
            return
        # Schedule 8 days after code_entry_date at 7 AM CT
        now = timezone.now()
        send_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
        if now.hour >= 7:
            send_time += timedelta(days=1)
        participant.send_email('wave1_survey_return', extra_context={'username': participant.user.username})
        participant.email_status = 'sent_wave1_survey_return'
        participant.save()
        logger.info(f"Sent wave1_survey_return to {participant.email}")
    except Participant.DoesNotExist:
        logger.error(f"Participant {participant_id} not found for wave1_survey_return")
    except Exception as e:
        logger.error(f"Error sending wave1_survey_return for participant {participant_id}: {str(e)}")
@shared_task
def send_wave1_monitoring_email(participant_id):
    """Send Wave 1 Physical Activity Monitoring email to participant."""
    """Information 10: Wave 1 Physical Activity Monitoring Ready"""
    try:
        participant = Participant.objects.get(id=participant_id)
        template = EmailTemplate.objects.get(name='wave1_monitor_ready')
        context = {'participant_id': participant.participant_id}
        body = template.body.format(**context)
        send_mail(
            template.subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [participant.email or participant.user.email, 'svu23@iastate.edu', 'vuleson59@gmail.com', 'projectpas2024@gmail.com'],
            fail_silently=False,
        )
        participant.email_status = 'sent'
        participant.email_send_date = timezone.now().date()
        participant.save()
        logger.info(f"Sent Wave 1 monitoring email to {participant.participant_id}")
    except Participant.DoesNotExist:
        logger.error(f"Participant {participant_id} not found")
    except EmailTemplate.DoesNotExist:
        logger.error("Wave 1 monitor ready email template not found")
    except Exception as e:
        logger.error(f"Failed to send Wave 1 monitoring email to {participant_id}: {e}")

@shared_task
def send_wave3_code_entry_email(participant_id):
    """Information 23: Physical Activity Monitoring Tomorrow (Wave 3)"""
    try:
        participant = Participant.objects.get(id=participant_id)
        
        # Calculate dates
        code_date = participant.wave3_code_entry_date
        if not code_date:
            logger.error(f"No Wave 3 code entry date for participant {participant_id}")
            return
            
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
def send_wave1_code_entry_email(participant_id):
    """Information 12: Physical Activity Monitoring Tomorrow (Wave 1)"""
    try:
        participant = Participant.objects.get(id=participant_id)
        # Check email_status to prevent duplicates
        if participant.email_status == 'sent_wave1_code':
            logger.info(f"Skipping wave1_code_entry for {participant.email}: already sent")
            return
        code_date = participant.code_entry_date
        if not code_date:
            logger.error(f"No code entry date for participant {participant_id}")
            return
        start_date = code_date + timedelta(days=1)
        end_date = code_date + timedelta(days=7)
        # Send immediately at 7 AM CT
        now = timezone.now()
        send_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
        if now.hour >= 7:
            send_time += timedelta(days=1)
        participant.send_email(
            'wave1_code_entry',
            extra_context={
                'username': participant.user.username,
                'code_date': code_date.strftime('%m/%d/%Y'),
                'start_date': start_date.strftime('%m/%d/%Y'),
                'end_date': end_date.strftime('%m/%d/%Y'),
            }
        )
        participant.email_status = 'sent_wave1_code'
        participant.save()
        logger.info(f"Sent wave1_code_entry to {participant.email}")
    except Participant.DoesNotExist:
        logger.error(f"Participant {participant_id} not found for wave1_code_entry")
    except Exception as e:
        logger.error(f"Error sending wave1_code_entry for participant {participant_id}: {str(e)}")
# @shared_task
# def send_wave1_code_entry_email(participant_id):
#     """Information 12: Physical Activity Monitoring Tomorrow (Wave 1)"""
#     try:
#         participant = Participant.objects.get(id=participant_id)
#         if participant.email_status == 'sent_wave1_code':
#             logger.info(f"Skipping wave1_code_entry for {participant.email}: already sent")
#             return
#         code_date = participant.code_entry_date
#         start_date = code_date + timedelta(days=1)
#         end_date = code_date + timedelta(days=7)
#         participant.send_email(
#             'wave1_code_entry',
#             extra_context={
#                 'username': participant.user.username,
#                 'code_date': code_date.strftime('%m/%d/%Y'),
#                 'start_date': start_date.strftime('%m/%d/%Y'),
#                 'end_date': end_date.strftime('%m/%d/%Y'),
#             }
#         )
#         participant.email_status = 'sent_wave1_code'
#         participant.save()
#         logger.info(f"Sent wave1_code_entry to {participant.email}")
#     except Participant.DoesNotExist:
#         logger.error(f"Participant {participant_id} not found for wave1_code_entry")
#     except Exception as e:
#         logger.error(f"Error sending wave1_code_entry for participant {participant_id}: {str(e)}")
""" @shared_task
def send_specific_email(participant_id, template_name, extra_context=None):
    try:
        participant = Participant.objects.get(id=participant_id)
        logger.info(f"Attempting to send {template_name} to {participant.email}")
        participant.send_email(template_name, extra_context)
        logger.info(f"Sent {template_name} to {participant.email}")
    except Participant.DoesNotExist:
        logger.error(f"Participant {participant_id} not found for {template_name}")
    except Exception as e:
        logger.error(f"Error sending {template_name} for participant {participant_id}: {e}") """
# @shared_task
# def send_specific_email(participant_id, template_name, extra_context=None):
#     try:
#         participant = Participant.objects.get(id=participant_id)
#         logger.info(f"Attempting to send {template_name} to {participant.email}")
#         participant.send_email(template_name, extra_context)
#         logger.info(f"Sent {template_name} to {participant.email}")
#     except Participant.DoesNotExist:
#         logger.error(f"Participant {participant_id} not found for {template_name}")
#     except Exception as e:
#         logger.error(f"Error sending {template_name} for participant {participant_id}: {e}")
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

# @shared_task
# def schedule_timeline_emails(participant_id):
#     """Schedule all timeline emails for a participant based on their enrollment date."""
#     try:
#         participant = Participant.objects.get(id=participant_id)
#         if not participant.is_confirmed:
#             logger.info(f"Skipping timeline email scheduling for {participant.participant_id}: not confirmed")
#             return

#         # Get the enrollment date
#         enrollment_date = participant.enrollment_date
#         if not enrollment_date:
#             logger.error(f"No enrollment date for {participant.participant_id}")
#             return

#         # Schedule Wave 1 monitoring email (Day 11)
#         send_wave1_monitoring_email.apply_async(
#             (participant_id,),
#             eta=timezone.datetime.combine(enrollment_date + timedelta(days=10), timezone.datetime.min.time().replace(hour=7))
#         )

#         # Schedule Wave 1 code entry reminder (Day 21)
#         send_wave1_code_entry_email.apply_async(
#             (participant_id,),
#             eta=timezone.datetime.combine(enrollment_date + timedelta(days=20), timezone.datetime.min.time().replace(hour=7))
#         )

#         # Schedule Wave 2 survey email (Day 57)
#         send_specific_email.apply_async(
#             (participant_id, 'wave2_survey_ready'),
#             eta=timezone.datetime.combine(enrollment_date + timedelta(days=56), timezone.datetime.min.time().replace(hour=7))
#         )

#         # Schedule Wave 2 no monitoring email (Day 67)
#         send_specific_email.apply_async(
#             (participant_id, 'wave2_no_monitoring'),
#             eta=timezone.datetime.combine(enrollment_date + timedelta(days=66), timezone.datetime.min.time().replace(hour=7))
#         )

#         # Schedule Wave 3 survey email (Day 85)
#         send_specific_email.apply_async(
#             (participant_id, 'wave3_survey_ready'),
#             eta=timezone.datetime.combine(enrollment_date + timedelta(days=84), timezone.datetime.min.time().replace(hour=7))
#         )

#         # Schedule Wave 3 monitoring email (Day 95)
#         send_specific_email.apply_async(
#             (participant_id, 'wave3_monitoring_ready'),
#             eta=timezone.datetime.combine(enrollment_date + timedelta(days=94), timezone.datetime.min.time().replace(hour=7))
#         )

#         logger.info(f"Scheduled all timeline emails for participant {participant.participant_id}")
#     except Participant.DoesNotExist:
#         logger.error(f"Participant {participant_id} not found for timeline email scheduling")
#     except Exception as e:
#         logger.error(f"Error scheduling timeline emails for participant {participant_id}: {str(e)}")

# def schedule_email(participant_entry):
#     from datetime import timedelta
#     send_date = participant_entry.entry_date + timedelta(days=0)
#     send_date = send_date.replace(hour=0, minute=0, second=10, microsecond=0)
#     send_scheduled_email_task.apply_async((participant_entry.participant_id,), eta=send_date)