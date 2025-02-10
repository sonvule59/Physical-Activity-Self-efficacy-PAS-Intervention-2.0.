import datetime
from django.db import models, migrations
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from .tasks.tasks.email_tasks import schedule_email
from testpas import settings
import string
import random
import uuid
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from sendgrid import SendGridAPIClient

class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    # created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.title

class Question(models.Model):
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)
    # created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.question_text

class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    # created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.user} - {self.question}"

class UserSurveyProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    progress = models.IntegerField(default=0)
    day_1 = models.DateField(null=True, blank=True)  # Represents Day 1 (date of consent)
    survey_completed = models.BooleanField(default=False)
    eligible = models.BooleanField(default=False)
    eligibility_reason = models.TextField(null=True, blank=True)  # Reason for eligibility or ineligibility
    consent_given = models.BooleanField(default=False)  # Whether consent has been provided
    progress_percentage = models.IntegerField(null=True, blank=True)  # Percentage of survey completed


    def __str__(self):
        return f"{self.user} - {self.survey} - {self.progress}%"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    confirmation_token = models.CharField(max_length=64, null=True, blank=True)
    token_expiration = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.user.username
    
class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField
    enrollment_date = models.DateField(default=timezone.now)
    code_entered = models.BooleanField(default=False)
    code_entry_date = models.DateField(null=True, blank=True)
    email_send_date = models.DateField(null=True, blank=True)  # store email send date
    email_status = models.CharField(max_length=50, default='pending')
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    # Double-blind Randomization
    participant_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    group = models.IntegerField(null=True, blank=True)
    group_assigned = models.BooleanField(default=False)
    intervention_start_date = models.DateTimeField(null=True, blank=True)
    intervention_end_date = models.DateTimeField(null=True, blank=True)
    engagement_tracked = models.BooleanField(default=False)
    email = models.EmailField(null=True, blank=True)  
    
    def __str__(self):
        return self.participant_id
    
    def save(self, *args, **kwargs):
        if self.code_entry_date and not self.email_send_date:
            self.email_send_date = self.code_entry_date + timezone.timedelta(days=8)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
    def send_code_entry_email(self):
        subject = "Physical Activity Monitoring Tomorrow (Wave 1)"
        message = f"""
        Hi {self.user.username},

        You have successfully entered the access code for physical activity monitoring. Thank you!

        Please start wearing the monitor tomorrow for seven consecutive days. For example, if you enter the code on {self.code_entry_date.strftime('%m/%d/%Y')} (Fri), please wear the device starting on {(self.code_entry_date + timedelta(days=1)).strftime('%m/%d/%Y')} (Sat) and continue wearing it until {(self.code_entry_date + timedelta(days=7)).strftime('%m/%d/%Y')} (Fri).

        To earn $35 in Amazon gift cards, please wear the monitor for at least 4 days, including one weekend day, with at least 10 hours each day. For the following seven days, complete the daily log at the end of each day. You will receive your total incentives after the study ends.

        If you need any assistance or have any questions at any time, please contact Seungmin (“Seung”) Lee (Principal Investigator) at seunglee@iastate.edu or 517-898-0020.

        Sincerely,

        The Obesity and Physical Activity Research Team
        """
        send_mail(
            subject,
            message,
            'projectpas2024@gmail.com',
            [self.user.email, 'projectpas2024@gmail.com'],
            fail_silently=False,
        )
        self.email_sent = True
        self.save()
    
    def check_email_status(self):
        if not self.message_id:
            return 'no_message_id'
            
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.client.messages._(self.message_id).get()
            
            if response.status_code == 200:
                status_data = response.to_dict
                if status_data.get('status') == 'delivered':
                    self.email_status = 'delivered'
                    self.save()
                return status_data.get('status')
            return 'check_failed'
        except Exception as e:
            return f'error: {str(e)}'

    def send_missing_code_email(self):
        subject = "Missing Code Entry (Wave 1)"
        message = f"""
        Hi {self.user.username},

        You missed the code entry (i.e., no $35 worth of Amazon electronic gift cards). However, you will still have more tasks in the future. We will contact you via email, so please regularly check your inbox.

        If you need any assistance or have any questions at any time, please contact Seungmin (“Seung”) Lee (Principal Investigator) at seunglee@iastate.edu or 517-898-0020.

        Sincerely,

        The Obesity and Physical Activity Research Team
        """
        send_mail(
            subject,
            message,
            'vuleson59@gmail.com',
            [self.user.email],
            fail_silently=False,
        )
        self.email_sent = True
        self.save()

#Testing
class ParticipantEntry(models.Model):
    participant_id = models.CharField(max_length=100)
    entry_date = models.DateTimeField(default=timezone.now)
    email = models.EmailField()

    def __str__(self):
        return self.participant_id

class EmailContent(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.subject
# @receiver(post_save, sender=ParticipantEntry)
# def schedule_email_on_entry(sender, instance, created, **kwargs):
#     if created:
#         schedule_email(instance)

class MessageContent(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sms_body = models.TextField()

    def __str__(self):
        return self.subject
    
class Token(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    #### Keep track of when the token was created ####
    created_at = models.DateTimeField(auto_now_add=True)
    # created_at = models.DateTimeField(default=timezone.now)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Token for {self.recipient.username}"

    @staticmethod
    def generate_token(length=10):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)


