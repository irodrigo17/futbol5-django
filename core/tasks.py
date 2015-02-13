import os
from datetime import datetime, timedelta
from celery import Celery
from django.conf import settings
from celery.schedules import crontab


##### celery app setup #####

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futbol5.settings')

# create celery app
app = Celery('fobal')

# app.conf.CELERY_IMPORTS = ('futbol.tasks', )
app.conf.BROKER_URL = os.environ['BROKER_URL']
app.conf.CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']
app.conf.CELERY_TASK_SERIALIZER = 'json'
app.conf.CELERY_ACCEPT_CONTENT = ['json']
app.conf.CELERYBEAT_SCHEDULE = {
    # Executes every Monday morning at 8:00 A.M
    'check-celery-every-5-seconds': {
        'task': 'core.tasks.check_celery',
        'schedule': timedelta(seconds=5),
    },
    'create-matches-and-send-emails-every-monday': {
        'task': 'core.tasks.create_matches_and_email_players',
        'schedule': crontab(hour=8, minute=00, day_of_week=1),
    },
}


from core.models import Player, Match, MatchPlayer
from core import mailer

##### helper methods #####

def next_weekday(date, weekday):
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return date + timedelta(days_ahead)


def default_weekdays_and_times():
    # TODO: store default weekdays and times somewhere else
    # so they can be easily changed using django admin
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


##### celery tasks #####

@app.task
def check_celery():
    # TODO: remove this task, only for debugging purposes
    player_count = Player.objects.count()
    match_count = Match.objects.count()
    print('just checking celery is working properly...')
    print('%d matches and %d players right now' % (match_count, player_count))


@app.task
def create_matches_and_email_players():
    matches = create_matches()
    players = Player.objects.all()
    mailer.send_invite_mails(matches, players)
