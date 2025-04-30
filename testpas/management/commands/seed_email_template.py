# testpas/management/commands/seed_email_templates.py
from django.core.management.base import BaseCommand
from testpas.models import EmailTemplate

EMAIL_TEMPLATES = [
    {
        "name": "account_confirmation",
        "subject": "Confirm Your PAS 2.0 Account",
        "body": "Dear {participant_id},\n\nPlease confirm your email by clicking the following link:\n{confirmation_link}\n\nThank you,\nPAS 2.0 Team"
    },
    {
        "name": "wave1_survey_ready",
        "subject": "Wave 1 Online Survey Set – Ready",
        "body": "Hi {username},\n\nCongratulations! You are now enrolled as a participant in the study.\n\nYour next task is to complete the Wave 1 Online Survey Set within 10 days. Instructions will follow soon.\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave1_monitor_ready",
        "subject": "Wave 1 Physical Activity Monitoring – Ready",
        "body": "Dear {participant_id},\n\nIt’s time for the first monitoring period. Please wear the provided device for 7 days.\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave1_code_entry",
        "subject": "Physical Activity Monitoring Tomorrow (Wave 1)",
        "body": "Hi {username},\n\nYou have successfully entered the access code for physical activity monitoring. Thank you!\n\nPlease start wearing the monitor tomorrow ({start_date}) for seven consecutive days until {end_date}.\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave1_survey_return",
        "subject": "Survey by Today & Return Monitor (Wave 1)",
        "body": "Dear {participant_id},\n\nPlease complete a short survey and return the monitor by today.\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave1_missing_code",
        "subject": "Missing Code Entry (Wave 1)",
        "body": "Hi {username},\n\nWe noticed you haven't entered your Wave 1 code. Please do so by today if you haven't.\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "intervention_access_later",
        "subject": "Intervention Access Later",
        "body": "Dear {participant_id},\n\nYou have been assigned to Group 0. You will receive intervention access later.\n{login_link}\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "intervention_access_immediate",
        "subject": "Intervention Access Immediately",
        "body": "Dear {participant_id},\n\nYou have been assigned to Group 1. You now have immediate access to the intervention.\n{login_link}\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave2_survey_ready",
        "subject": "Wave 2 Online Survey Set – Ready",
        "body": "Dear {participant_id},\n\nYour Wave 2 online survey is now available. Please complete it soon.\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave2_no_monitoring",
        "subject": "No Wave 2 Physical Activity Monitoring",
        "body": "Dear {participant_id},\n\nThere is no physical activity monitoring for Wave 2. Just complete the survey.\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave3_survey_ready",
        "subject": "Wave 3 Online Survey Set – Ready",
        "body": "Dear {participant_id},\n\nYour Wave 3 online survey is now available. Please complete it soon.\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave3_monitoring_ready",
        "subject": "Wave 3 Physical Activity Monitoring – Ready",
        "body": "Dear {participant_id},\n\nIt’s time for the final monitoring period. Please wear the device for 7 days.\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave3_code_entry",
        "subject": "Physical Activity Monitoring Tomorrow (Wave 3)",
        "body": "Dear {participant_id},\n\nStarting tomorrow ({start_date}), please wear the device for 7 days until ({end_date}).\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave3_survey_monitor_return",
        "subject": "Survey by Today & Return Monitor (Study End)",
        "body": "Dear {participant_id},\n\nPlease complete a short survey and return the monitor by today.\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave3_missing_code",
        "subject": "Missing Code Entry (Study End)",
        "body": "Dear {participant_id},\n\nYou missed the Wave 3 code entry. No further action is required.\n{login_link}\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "study_end",
        "subject": "PAS 2.0 Study Concluded",
        "body": "Dear {participant_id},\n\nThank you for participating in the PAS 2.0 study. The study has now concluded.\n\nBest,\nPAS 2.0 Team"
    },
]

class Command(BaseCommand):
    help = "Seeds the database with default email templates."

    def handle(self, *args, **kwargs):
        for template in EMAIL_TEMPLATES:
            obj, created = EmailTemplate.objects.get_or_create(
                name=template["name"],
                defaults={'subject': template["subject"], 'body': template["body"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added email template: {template['name']}"))
            else:
                # Update existing template to ensure correct subject and body
                obj.subject = template["subject"]
                obj.body = template["body"]
                obj.save()
                self.stdout.write(self.style.WARNING(f"Updated template: {template['name']}"))