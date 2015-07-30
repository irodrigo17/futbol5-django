"""
Module containing recurring tasks and helper functions.
"""

import logging
from datetime import datetime, timedelta
from core.models import Player, Match, WeeklyMatchSchedule
from core import mailer, datehelper


LOGGER = logging.getLogger(__name__)


def create_match_or_send_status(date, async):
    """
    Creates next match and sends invite emails if needed, or sends status emails
    if the next match is already created.
    Matches are played according to the existing WeeklyMatchSchedule instances.
    No matches are created and no emails are sent on weekends.
    Returns the found or created match if any.
    If async si true emails are sent asynchronously.
    """
    if datehelper.is_weekend(date):
        # nothing happens on weekends
        LOGGER.info('No emails sent on weekends %s' % date)
        return None
    else:
        # find next match
        next_match = Match.next_match(date)
        if next_match == None:
            # create next match according to the schedule if needed
            schedule = WeeklyMatchSchedule.invite_weekday_schedule(date)
            if schedule == None:
                LOGGER.info('No weekly match schedules setup to send invites on %s' % date)
                return None
            else:
                next_match = schedule.create_next_match(date)
                sent_mails = mailer.send_invite_mails(next_match, Player.objects.all(), async)
                LOGGER.info('Created match for %s and sent %i invitation emails' % (next_match.date, sent_mails))
        else:
            sent_mails = mailer.send_status_mails(next_match, Player.objects.all(), async)
            LOGGER.info('Sent %i status messages for next match: %s' % (sent_mails, next_match.date))

        return next_match
