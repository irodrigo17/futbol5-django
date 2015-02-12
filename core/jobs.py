from core.models import Player, Match, MatchPlayer
from datetime import datetime, timedelta


def next_weekday(date, weekday):
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return date + timedelta(days_ahead)


def default_weekdays_and_times():
    # TODO: store default weekdays and times somewhere else
    # so they ca be easily changed using django admin
    return [{'weekday': 2, 'hour': 19}, {'weekday': 4, 'hour': 20}]


def week_dates(start_date, weekdays_and_times):
    dates = []
    for weekday_time in weekdays_and_times:
        date = next_weekday(start_date, weekday_time['weekday'])
        date = date.replace(hour=weekday_time['hour'], minute=0, second=0, microsecond=0)
        dates.append(date)

    return dates


def default_place():
    # TODO: store default place somewhere else so it can be
    # easily changed using django admin
    return 'River'


def create_matches():
    """
    creates matches for this week, at the default weekdays, times and places
    """

    dates = week_dates(datetime.now(), default_weekdays_and_times())
    place = default_place()

    matches = []
    for date in dates:
        match = Match.objects.create(date=date, place=place)
        matches.append(match)

    return matches


def email_players(matches):
    # TODO: implement me
    return False
