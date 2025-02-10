from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ParticipantEntry
from .tasks.email_tasks import schedule_email  # Update import path

@receiver(post_save, sender=ParticipantEntry)
def schedule_email_on_entry(sender, instance, created, **kwargs):
    if created:
        schedule_email(instance)