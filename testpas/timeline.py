import datetime
from django.utils.timezone import make_aware, is_naive, now as tz_now

def get_day_difference(start_time, now=None):
    """ Calculate the difference in days between two datetime objects.
        If `now` is not provided, it defaults to the current time."""
    ### Jun 25: Add in timezone aware datetime objects
    now = now or tz_now()
    if is_naive(start_time):
        start_time = make_aware(start_time)
    return (now - start_time).days

def get_day_difference_compressed(start_time, now=None, seconds_per_day=86400):
    """86400 seconds = 1 real-world day (24 hours * 60 minutes * 60 seconds). We can adjust this for testing purposes. We will do this
    this way to make sure it works."""
    ### Jun 25: Add in timezone aware datetime objects
    now = now or tz_now()
    if is_naive(start_time):
        start_time = make_aware(start_time)
    seconds_elapsed = (now - start_time).total_seconds()
    return int(seconds_elapsed // seconds_per_day)


def get_timeline_day(user, now=None, compressed=False, seconds_per_day=15):
    if not user.date_joined:
        return None
    if compressed:
        return get_day_difference_compressed(user.date_joined, now, seconds_per_day)
    return get_day_difference(user.date_joined, now)