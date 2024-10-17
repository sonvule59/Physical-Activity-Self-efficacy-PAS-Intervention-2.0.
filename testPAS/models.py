from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.db import models
import string
import random
import uuid

class Token(models.Model):
    # recipient = models.CharField(max_length=255)
    # token = models.CharField(max_length=10, unique=True)
    # created_at = models.DateTimeField(auto_now_add=True)

    recipient = models.CharField(max_length=100)
    token = models.CharField(max_length=100, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Token for {self.recipient}: {self.token}"

    @staticmethod
    def generate_token(length=6):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)

class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)

class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class UserSurveyProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    progress = models.IntegerField(default=0)
