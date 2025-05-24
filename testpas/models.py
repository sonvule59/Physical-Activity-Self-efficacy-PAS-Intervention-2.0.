import datetime
from django.db import models, migrations
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta
from testpas import settings
import string
import random
import uuid
from django.core.mail import send_mail
from django.conf import settings
from testpas import settings

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

class CustomUser(AbstractUser):
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    registration_code = models.CharField(max_length=15, null=True, blank=True)
    consented = models.BooleanField(null=True, blank=True)
    consent_response = models.TextField(null=True, blank=True)

    # Avoid conflicts with default 'User' model by adding related_name
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_set",
        blank=True,
        help_text="Specific permissions for this user.",
    )
class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    # created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.user} - {self.question}"
class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=255)
    body = models.TextField(help_text="Use {participant_id} as placeholder.")
    def __str__(self):
        return self.name
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

    def __str__(self):
        return self.user.username
    
def generate_confirmation_token():
    return uuid.uuid4().hex

class Participant(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    enrollment_date = models.DateField(default=timezone.now)
    code_entered = models.BooleanField(default=False)
    code_entry_date = models.DateField(null=True, blank=True)
    email_send_date = models.DateField(null=True, blank=True)  # store email send date
    email_status = models.CharField(max_length=50, default='pending')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    confirmation_token = models.CharField(max_length=255, unique=True)
    is_confirmed = models.BooleanField(default=False)
    token_expiration = models.DateTimeField(default=timezone.now)
    phase = models.CharField(max_length=100, blank=True, null=True)
    monitoring_start_date = models.DateField(blank=True, null=True)
    # Double-blind Randomization
    participant_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    group = models.IntegerField(null=True, blank=True)
    group_assigned = models.BooleanField(default=False)
    intervention_start_date = models.DateTimeField(null=True, blank=True)
    intervention_end_date = models.DateTimeField(null=True, blank=True)
    engagement_tracked = models.BooleanField(default=False)
    email = models.EmailField(null=True, blank=True)  
    wave3_code_entered = models.BooleanField(default=False)  # New field for Wave 3
    wave3_code_entry_date = models.DateField(null=True, blank=True)
    
    
    def save(self, *args, **kwargs):
        if not self.confirmation_token:
            self.confirmation_token = uuid.uuid4().hex
            while Participant.objects.filter(confirmation_token=self.confirmation_token).exists():
                self.confirmation_token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def send_email(self, template_name, extra_context=None):
            template = EmailTemplate.objects.get(name=template_name)
            context = {'participant_id': self.participant_id, 'username': self.user.username}
            if extra_context:
                context.update(extra_context)
            body = template.body.format(**context)
            try:
                send_mail(
                    template.subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.email or self.user.email, 'vuleson59@gmail.com', 'projectpas2024@gmail.com'],
                    fail_silently=False,
                )
                self.email_status = 'sent'
                self.email_send_date = timezone.now().date()
                self.save()
            except Exception as e:
                self.email_status = 'failed'
                self.save()
                raise

    # def send_email(self, template_name, extra_context=None, mark_as=None):
    #     if mark_as and self.email_status == mark_as:
    #         return
    #     try:
    #         template = EmailTemplate.objects.get(name=template_name)
    #     except EmailTemplate.DoesNotExist:
    #         self.email_status = 'failed'
    #         self.save()
    #         raise
    #     context = {'participant_id': self.participant_id, 'username': self.user.username}
    #     if extra_context:
    #         context.update(extra_context)
    #     try:
    #         body = template.body.format(**context)
    #         send_mail(
    #             template.subject,
    #             body,
    #             settings.DEFAULT_FROM_EMAIL,
    #             # FIX 2: Standardized recipients to match PAS document
    #             [self.email or self.user.email, 'vuleson59@gmail.com', 'projectpas2024@gmail.com'],
    #             fail_silently=False,
    #         )
    #         self.email_status = mark_as or 'sent'
    #         self.email_send_date = timezone.now().date()
    #         self.save()
    #     except Exception as e:
    #         self.email_status = 'failed'
    #         self.save()
    #         raise


    def send_confirmation_email(self):
        confirmation_link = f"{settings.BASE_URL}/confirm-account/{self.confirmation_token}/"
        self.send_email(
            'account_confirmation',
            extra_context={'confirmation_link': confirmation_link},
            mark_as='sent_confirmation'
        )
    # def send_confirmation_email(self):
    #     from django.core.mail import send_mail
    #     template = EmailTemplate.objects.get(name='account_confirmation')
    #     subject = template.subject
    #     confirmation_link = f"http://localhost:8000/confirm/{self.confirmation_token}/"
    #     message = template.body.format(participant_id=self.participant_id, confirmation_link=confirmation_link)
    #     send_mail(subject, message, 'projectpas2024@gmail.com', [self.email])

    def __str__(self):
        return self.participant_id
    def __str__(self):
        return self.user.username
    
    """Info 12"""
    def send_code_entry_email(self):
        template = EmailTemplate.objects.get(name='wave1_code_entry')
        message = template.body.format(
            username=self.user.username,
            code_date=self.code_entry_date.strftime('%m/%d/%Y'),
            start_date=(self.code_entry_date + timedelta(days=1)).strftime('%m/%d/%Y'),
            end_date=(self.code_entry_date + timedelta(days=7)).strftime('%m/%d/%Y')
        )
    
        
    def send_wave1_survey_return_email(self):
        template = EmailTemplate.objects.get(name='wave1_survey_return')
        message = template.body.format(participant_id=self.participant_id)
        send_mail(
            template.subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email, 'vuleson59@gmail.com', 'projectpas2024@gmail.com'],
            fail_silently=False,
        )
        self.email_status = 'sent'
        self.email_send_date = timezone.now().date()
        self.save()

    def send_wave2_survey_email(self):
        template = EmailTemplate.objects.get(name='wave2_survey_ready')
        subject = template.subject
        message = template.body.format(participant_id=self.participant_id)
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.user.email, 'vuleson59@gmail.com', 'projectpas2024@gmail.com'],
                fail_silently=False,
            )
            self.email_status = 'sent'
            self.email_send_date = timezone.now().date()
            self.save()
            return True
        except Exception as e:
            print(f"Wave 2 email error: {str(e)}")
            self.email_status = 'failed'
            self.save()
            return False
    def send_missing_code_email(self):  # Info 14
        template = EmailTemplate.objects.get(name='wave1_missing_code')
        message = template.body.format(username=self.user.username)
        send_mail(template.subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email, 'vuleson59@gmail.com'], fail_silently=False)
        self.email_status = 'sent'
        self.email_send_date = timezone.now().date()
        self.save()
    def send_wave2_no_monitoring_email(self):  # Info 16 & 19
        template = EmailTemplate.objects.get(name='intervention_access_later' if self.group == 0 else 'wave2_no_monitoring')
        message = template.body.format(participant_id=self.participant_id)
        send_mail(template.subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email, 'vuleson59@gmail.com'], fail_silently=False)
        self.email_status = 'sent'
        self.email_send_date = timezone.now().date()
        self.save()

    def send_wave2_survey_email(self):  # Info 17 & 18
        template = EmailTemplate.objects.get(name='intervention_access_immediate' if self.group == 1 and self.intervention_start_date == timezone.now().date() else 'wave2_survey_ready')
        message = template.body.format(participant_id=self.participant_id)
        send_mail(template.subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email, 'vuleson59@gmail.com'], fail_silently=False)
        self.email_status = 'sent'
        self.email_send_date = timezone.now().date()
        self.save()

    def send_wave3_survey_email(self):  # Info 20
        template = EmailTemplate.objects.get(name='wave3_survey_ready')
        message = template.body.format(participant_id=self.participant_id)
        send_mail(template.subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email, 'vuleson59@gmail.com'], fail_silently=False)
        self.email_status = 'sent'
        self.email_send_date = timezone.now().date()
        self.save()
    def send_wave3_monitoring_email(self):  # Info 21
        template = EmailTemplate.objects.get(name='wave3_monitoring_ready')
        message = template.body.format(participant_id=self.participant_id)
        send_mail(template.subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email, 'vuleson59@gmail.com'], fail_silently=False)
        self.email_status = 'sent'
        self.email_send_date = timezone.now().date()
        self.save()

    def send_wave3_code_entry_email(self):  # Info 23
        template = EmailTemplate.objects.get(name='wave3_code_entry')
        message = template.body.format(participant_id=self.participant_id, code_date=self.wave3_code_entry_date.strftime('%m/%d/%Y'), start_date=(self.wave3_code_entry_date + timezone.timedelta(days=1)).strftime('%m/%d/%Y'), end_date=(self.wave3_code_entry_date + timezone.timedelta(days=7)).strftime('%m/%d/%Y'))
        send_mail(template.subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email, 'vuleson59@gmail.com'], fail_silently=False)
        self.email_status = 'sent'
        self.email_send_date = timezone.now().date()
        self.save()

    def send_study_end_email(self):  # Info 24
        template = EmailTemplate.objects.get(name='study_end')
        message = template.body.format(participant_id=self.participant_id)
        send_mail(template.subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email, 'vuleson59@gmail.com'], fail_silently=False)
        self.email_status = 'sent'
        self.email_send_date = timezone.now().date()
        self.save()

    def send_wave3_missing_code_email(self):  # Info 25
        template = EmailTemplate.objects.get(name='wave3_missing_code')
        message = template.body.format(participant_id=self.participant_id)
        send_mail(template.subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email, 'vuleson59@gmail.com'], fail_silently=False)
        self.email_status = 'sent'
        self.email_send_date = timezone.now().date()
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
    
class Challenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    code = models.CharField(max_length=255, null=True, blank=True)  # For challenges requiring a code
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    completed = models.BooleanField(default=False)

class SurveyProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interest_submitted = models.BooleanField(default=False)
    interested = models.BooleanField(null=True, blank=True)

    eligibility_submitted = models.BooleanField(default=False)
    is_eligible = models.BooleanField(null=True, blank=True)

    consent_submitted = models.BooleanField(default=False)
    consented = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"SurveyProgress for {self.user.username}"
    
class Token(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Token for {self.recipient.username}"

    @staticmethod
    def generate_token(length=25):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)


