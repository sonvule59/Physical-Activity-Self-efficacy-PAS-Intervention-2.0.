import json
from hashlib import sha256
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
import datetime
from django.http import JsonResponse
from .models import *
import random
import string

def generate_token():
    """Generate a unique token and its hash."""
    token = get_random_string(64)
    token_hash = sha256(token.encode()).hexdigest()
    return token, token_hash

def send_confirmation_email(user, token):
    """Send a confirmation email to the user."""
    confirmation_url = f"{settings.BASE_URL}/confirm-account/?token={token}"
    email_body = f"""
    Thank you for registering. Please confirm your account by clicking the link below:
    
    {confirmation_url}
    
    Your confirmation code: {token}
    """
    send_mail(
        'Confirm your account',
        email_body,
        settings.DEFAULT_FROM_EMAIL,  # Use the verified "from" email address
        [user.email],
        fail_silently=False,
    )

def json_response(data, status=200):
    """Create a JsonResponse with the given data and status code."""
    return JsonResponse(data, status=status)

from django.utils import timezone
from hashlib import sha256

def validate_token(token, user_profile):
    """Validate the token for the user profile."""
    token_hash = sha256(token.encode()).hexdigest()
    return (
        user_profile.confirmation_token == token_hash and
        user_profile.token_expiration >= timezone.now()
    )

""" OLD VALIDATE TOKEN
def validate_token(token, user_profile):
    #Validate the token for the user profile.
    token_hash = sha256(token.encode()).hexdigest()
    return Participant.confirmation_token == token_hash and Participant.token_expiration >= datetime.datetime.now()
"""
# ADDED TO MAKE TIME CONTROLS MORE CLEAR

from django.utils import timezone

# DEV TIME CONTROL
_fake_time = None

def get_current_time():
    """Returns fake time if set, otherwise real current time."""
    return _fake_time or timezone.now()

def set_fake_time(fake_datetime):
    """Set a fake current time (for testing/timeline debugging)."""
    global _fake_time
    _fake_time = fake_datetime

def clear_fake_time():
    """Reset to real time."""
    global _fake_time
    _fake_time = None

def get_fake_time():
    """Return the current fake time, if any."""
    return _fake_time
