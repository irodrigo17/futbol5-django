"""
Helper module for handling dates.
"""

from datetime import datetime, timedelta


FRIDAY = 4


def next_date(date, weekday):
    """
    Return the first date corresponding to the given weekday that comes after the given date.
    """
    days_ahead = weekday - date.weekday()
    if days_ahead < 0:
        # Target day already happened this week
        days_ahead += 7
    return date + timedelta(days=days_ahead)


def set_time(date, time):
    """
    Return a new date by setting the given time to the given date.
    """
    return date.replace(hour=time.hour, minute=time.minute, second=time.second, microsecond=time.microsecond)


def is_weekend(date):
    """
    Return true if the given date is Saturday or Sunday, and false otherwise.
    """
    return date.weekday() > FRIDAY
