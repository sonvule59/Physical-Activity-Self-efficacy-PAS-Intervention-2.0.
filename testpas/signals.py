from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from .tasks.tasks.email_tasks import schedule_email  # Update import path

@receiver(post_save, sender=ParticipantEntry)
def schedule_email_on_entry(sender, instance, created, **kwargs):
    if created:
        Participant.objects.create(user=instance)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Participant.objects.create(user=instance)