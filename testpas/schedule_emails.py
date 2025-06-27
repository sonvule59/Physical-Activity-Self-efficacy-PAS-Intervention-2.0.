# testpas/schedule_emails.py
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from testpas.models import Participant, UserSurveyProgress
from testpas.tasks import send_wave1_monitoring_email
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

# FIXED SNIPPET START: Schedule Wave 1 monitoring email
@shared_task
def schedule_wave1_monitoring_email(participant_id):
    """Schedule Wave 1 Physical Activity Monitoring email for Day 11 or 11 minutes in test mode."""
    try:
        participant = Participant.objects.get(id=participant_id)
        if not participant.is_confirmed or not UserSurveyProgress.objects.filter(user=participant.user, survey__title="Eligibility Criteria", consent_given=True).exists():
            logger.info(f"Skipping Wave 1 monitoring email for {participant.participant_id}: not confirmed or not consented")
            return
        
        progress = UserSurveyProgress.objects.filter(user=participant.user, survey__title="Eligibility Criteria").first()
        if not progress or not progress.day_1:
            logger.error(f"No day_1 set for {participant.participant_id}")
            return

        # Calculate send time (Day 11 at 7 AM CT)
        send_date = progress.day_1 + timedelta(days=10)  # Day 11
        send_time = timezone.datetime.combine(send_date, timezone.datetime.min.time().replace(hour=7, tzinfo=timezone.get_current_timezone()))
        
        # Apply time compression if TEST_MODE=True
        if getattr(settings, 'TEST_MODE', False):
            scale = getattr(settings, 'TEST_TIME_SCALE', 5)  # 1 day = 5 seconds
            minutes_to_add = 11 * scale  # 11 days -> 11 minutes
            send_time = timezone.now() + timedelta(minutes=minutes_to_add)
        
        # Schedule email
        send_wave1_monitoring_email(participant_id)
        logger.info(f"Scheduled Wave 1 monitoring email for {participant.participant_id} at {send_time}")
    except Participant.DoesNotExist:
        logger.error(f"Participant {participant_id} not found for scheduling")
# FIXED SNIPPET END