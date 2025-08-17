# testpas/management/commands/seed_email_templates.py
from django.core.management.base import BaseCommand
from testpas.models import EmailTemplate

EMAIL_TEMPLATES = [
    {
        "name": "account_confirmation",
        "subject": "Confirm Your PAS 2.0 Account",
        # "body": "Dear {participant_id},\n\nPlease confirm your email by clicking the following link:\n{confirmation_link}\n\nThank you,\nPAS 2.0 Team"
        "body": "Dear {username},\n\nPlease confirm your email by clicking the following link:\n{confirmation_link}\n\nThank you,\nPAS 2.0 Team"
    },
    {
        "name": "wave1_survey_ready",
        "subject": "Wave 1 Online Survey Set – Ready",
        "body": "Hi {username},\n\nCongratulations! You are now enrolled as a participant in the study.\n\nYour next task is to complete the Wave 1 Online Survey Set within 10 days. Instructions will follow soon.\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave1_monitor_ready",
        "subject": "Wave 1 Physical Activity Monitoring – Ready",
        "body": (
            # "Hi {participant_id},\n\n"
            "Hi {username},\n\n"
            "Your next task is to complete Wave 1 Physical Activity Monitoring.\n\n"
            "You need to meet with research members within 10 days to complete the physical activity monitoring. "
            "Within the next few days, research members will contact you to provide a physical activity monitor and instructions for wearing it. "
            "You will earn an additional $35 in your Amazon electronic gift card account for completing this task. "
            "You will receive the accrued incentives after this study ends. "
            "After 10 days, this task will expire (i.e., no Amazon gift card for this task).\n\n"
            "If you need any assistance or have any questions at any time, please contact Seungmin (“Seung”) Lee (Principal Investigator) "
            "at svu23@iastate.edu or 517-898-0020.\n\n"
            "Sincerely,\nThe Obesity and Physical Activity Research Team"
        )
    },
        {
            'name': 'wave1_code_entry',
            'subject': 'Physical Activity Monitoring Tomorrow (Wave 1)',
            'body': (
                'Hi {username},\n\n'
                'You have successfully entered the access code for physical activity monitoring. Thank you!\n\n'
                'Please start wearing the monitor tomorrow for seven consecutive days. For example, if you enter the code on {code_date} (Fri), '
                'please wear the device starting on {start_date} (Sat) and continue wearing it until {end_date} (Fri).\n\n'
                'To earn $35 in Amazon gift cards, please wear the monitor for at least 4 days, including one weekend day, with at least 10 hours each day. '
                'For the following seven days, complete the daily log at the end of each day. You will receive your total incentives after the study ends.\n\n'
                'If you need any assistance, contact Seungmin Lee at svu23@iastate.edu or 517-898-0020.\n\n'
                'Sincerely,\nThe Obesity and Physical Activity Research Team'
            )
        },
        {
            'name': 'wave1_survey_return',
            'subject': 'Survey by Today & Return Monitor (Wave 1)',
            'body': (
                'Hi {username},\n\n'
                'The timeline for wearing the physical activity monitor is complete for this wave.\n\n'
                'Your next two tasks are listed below:\n'
                '1. Please complete a short survey. This task must be done by today and should take approximately 10 minutes to complete.\n'
                '   Please click the following link to complete the task: {survey_link}\n\n'
                '2. Please return the monitor. Within a couple of days, research members will contact you to arrange the return.\n\n'
                'If you need any assistance, contact Seungmin Lee at svu23@iastate.edu or 517-898-0020.\n\n'
                'Sincerely,\nThe Obesity and Physical Activity Research Team'
            )
        },
        {
            'name': 'wave1_missing_code',
            'subject': 'Missing Code Entry (Wave 1)',
            'body': (
                'Hi {username},\n\n'
                'We noticed you haven not entered your Wave 1 physical activity monitoring code. '
                'Unfortunately, you have missed the opportunity to earn the $35 Amazon gift card for this monitoring period. '
                'However, you will still have more tasks in the future and can continue participating in the study.\n\n'
                'We will contact you via email for upcoming tasks, so please regularly check your inbox.\n\n'
                'If you need any assistance or have questions, please contact Seungmin Lee at svu23@iastate.edu or 517-898-0020.\n\n'
                'Sincerely,\nThe Obesity and Physical Activity Research Team'
            )
        },

    {
        "name": "intervention_access_later",
        "subject": "Intervention Access Later",
        "body": "Dear {username},\n\nYou have been assigned to Group 0. You will receive intervention access later.\nBest,\nPAS 2.0 Team"
        # "body": "Dear {participant_id},\n\nYou have been assigned to Group 0. You will receive intervention access later.\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "intervention_access_immediate",
        "subject": "Intervention Access Immediately",
        "body": (
            "Hi {username},\n\n"
            "Your access to the online physical activity intervention will begin immediately. "
            "You may access the online physical activity intervention whenever you wish throughout approximately 4 weeks.\n\n"
            "· Please log in from the following website: (***Login link placeholder, will be updated in production***)\n"
            "· Your ID is: {username}. If you forgot your password, you may reset it on the website.\n\n"
            "If you complete at least 24 post-introductory challenges during the 4 weeks, you will earn an additional $20 "
            "in your Amazon electronic gift card account. Thoughtfully completing at least 24 post-introductory challenges "
            "may take approximately 2 hours. You will receive the accrued incentives after this study ends.\n\n"
            "We will also email you again in approximately 4 weeks for the next task (i.e., completing an online survey set). "
            "Please regularly check your inbox. You will receive the accrued incentives after this study ends.\n\n"
            "If you need any assistance or have any questions at any time, please contact Seungmin (“Seung”) Lee "
            "(Principal Investigator) at svu23@iastate.edu or 517-898-0020.\n\n"
            "Sincerely,\n\n"
            "The Obesity and Physical Activity Research Team"
        )
    },
    {
        "name": "wave2_survey_ready",
        "subject": "Wave 2 Online Survey Set – Ready",
        "body": (
            "Hi {username},\n\n"
            "Your next task is to complete the Wave 2 Online Survey Set within 10 days. You will earn $5 in your Amazon electronic gift card account for completing this task. "
            "You will receive the accrued incentives after this study ends. After 10 days, this task will expire (i.e., no Amazon gift card for this task).\n"
            "· Please click the following link to complete the task: {survey_link}\n\n"
            "If you need any assistance or have any questions at any time, please contact Seungmin (“Seung”) Lee (Principal Investigator) at svu23@iastate.edu or 517-898-0020.\n\n"
            "Sincerely,\n"
            "The Obesity and Physical Activity Research Team"
        )
    },
        {
        "name": "wave2_no_monitoring",
        "subject": "No Wave 2 Physical Activity Monitoring",
        "body": (
            "Hi {username},\n\n"
            "There is no Wave 2 Physical Activity Monitoring.\n\n"
            "We will email you again in approximately 4 weeks for the next task (i.e., completing an online survey set). Please regularly check your inbox. You will receive the accrued incentives after this study ends.\n\n"
            "If you need any assistance or have any questions at any time, please contact Seungmin (“Seung”) Lee (Principal Investigator) at svu23@iastate.edu or 517-898-0020.\n\n"
            "Sincerely,\n"
            "The Obesity and Physical Activity Research Team"
        )
    },

    {
        "name": "wave3_survey_ready",
        "subject": "Wave 3 Online Survey Set – Ready",
        "body": (
            "Hi {username},\n\n"
            "Your next task is to complete the Wave 3 Online Survey Set within 10 days. You will earn $5 in your Amazon electronic gift card account for completing this task. "
            "You will receive the accrued incentives after this study ends. After 10 days, this task will expire (i.e., no Amazon gift card for this task).\n"
            "· Please click the following link to complete the task: {survey_link}\n\n"
            "If you need any assistance or have any questions at any time, please contact Seungmin (“Seung”) Lee (Principal Investigator) at svu23@iastate.edu or 517-898-0020.\n\n"
            "Sincerely,\n"
            "The Obesity and Physical Activity Research Team"
        )
    },
    {
        "name": "wave3_monitoring_ready",
        "subject": "Wave 3 Physical Activity Monitoring – Ready",
        "body": "Dear {username},\n\nIt’s time for the final monitoring period. Please wear the device for 7 days.\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave3_code_entry",
        "subject": "Physical Activity Monitoring Tomorrow (Wave 3)",
        "body": "Dear {username},\n\nStarting tomorrow ({start_date}), please wear the device for 7 days until ({end_date}).\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave3_survey_monitor_return",
        "subject": "Survey by Today & Return Monitor (Study End)",
        "body": "Dear {username},\n\nPlease complete a short survey and return the monitor by today.\n\nBest,\nPAS 2.0 Team"
    },
    {
        "name": "wave3_missing_code",
        "subject": "Missing Code Entry (Study End)",
        "body": (
            "Hi {username},\n\n"
            "We noticed you haven't entered your Wave 3 physical activity monitoring code. "
            "Unfortunately, you have missed the opportunity to earn the $40 Amazon gift card for this monitoring period. "
            "The study has now concluded, and you will no longer receive further tasks.\n\n"
            "If you were assigned to Group 0, you will now receive access to the intervention. "
            "Please check your email for intervention access instructions.\n\n"
            "If you need any assistance or have questions, please contact Seungmin Lee at svu23@iastate.edu or 517-898-0020.\n\n"
            "Sincerely,\nThe Obesity and Physical Activity Research Team"
        )
    },
    {
        "name": "study_end",
        "subject": "PAS 2.0 Study Concluded",
        "body": (
            "Hi {username},\n\n"
            "Thank you for participating in the PAS 2.0 study. The study has now concluded.\n\n"
            "Your final tasks are:\n"
            "1. Please complete a short survey. This task must be done by today and should take approximately 10 minutes to complete.\n"
            "   Please click the following link to complete the task: {survey_link}\n\n"
            "2. Please return the monitor. Within a couple of days, research members will contact you to arrange the return.\n\n"
            "If you were assigned to Group 0, you will now receive access to the intervention. "
            "Please check your email for intervention access instructions.\n\n"
            "If you need any assistance or have questions, please contact Seungmin Lee at svu23@iastate.edu or 517-898-0020.\n\n"
            "Sincerely,\nThe Obesity and Physical Activity Research Team"
        )
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