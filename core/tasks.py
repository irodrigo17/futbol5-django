import logging
from datetime import datetime, timedelta
from core.models import Player, Match
from core import mailer



DEFAULT_PLACE = 'River'


MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6


LOGGER = logging.getLogger(__name__)


def next_weekday(date, weekday):
    """
    Return the next date corresponding to the given weekday, starting from the
    given date.
    """
    days_ahead = weekday - date.weekday()
    if days_ahead < 0: # Target day already happened this week
        days_ahead += 7
    return date + timedelta(days_ahead)


def set_hour(date, hour):
    """
    Set the given hour to the given date and reset the rest ofthe time
    components to zero.
    """
    return date.replace(hour=hour, minute=0, second=0, microsecond=0)


def find_or_create_match(date):
    """
    Finds or creates a match for the given date.
    If the match exists, sends status emails to match players, else send
    invitation emails to all players.
    Returns the created or found match.
    """
    match = Match.objects.filter(date=date).first()

    if match == None:
        match = Match.objects.create(date=date, place=DEFAULT_PLACE)
        sent_mails = mailer.send_invite_mails(match, Player.objects.all())
        LOGGER.info('Created match for %s and sent %i invitation emails' % (match.date, sent_mails))
    else:
        sent_mails = mailer.send_status_mails(match)
        LOGGER.info('Sent %i status messages for next match: %s' % (sent_mails, match.date))

    return match


def create_match_or_send_status(date):
    """
    Creates next match and sends invite emails if needed, or sends status emails
    if the next match is already created.
    Matches are played on Wednesdays @ 19:00 and on Fridays @ 20:00.
    No matches are created and no emails are sent on weekends.
    Returns the found or created match if any.
    """
    weekday = date.weekday()
    if weekday > FRIDAY:
        # nothing happens on weekends
        LOGGER.info('No emails sent on %s' % date)
        return None
    else:
        next_wed = next_weekday(date, WEDNESDAY)
        next_wed = set_hour(next_wed, 19)

        next_fri = next_weekday(date, FRIDAY)
        next_fri = set_hour(next_fri, 20)

        earlier_date = min(next_wed, next_fri)
        later_date = max(next_wed, next_fri)

        if date < earlier_date:
            # find or create a match for next Wednesday
            match = find_or_create_match(earlier_date)
        else:
            # find or create a match for next Friday
            match = find_or_create_match(later_date)

    return match
