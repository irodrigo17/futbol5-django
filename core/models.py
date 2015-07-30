"""
Module for Django models.
"""

from datetime import datetime
from core import datehelper
from django.db import models
from django.core.validators import validate_email, MinValueValidator, MaxValueValidator
from django.db.models import Count, Q
from django.contrib.auth.models import User


class Player(models.Model):
    """
    Model class representing a player.
    A player has basic personal information like name and email.
    Name and email are required and unique.
    """

    name = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=50, unique=True, db_index=True, validators=[validate_email])
    matches = models.ManyToManyField('Match', through='MatchPlayer')
    user = models.ForeignKey(User, null=True, blank=True)

    def __str__(self):
        """
        Overriding to return the player name as the string representation.
        """
        return self.name

    @classmethod
    def top_player(cls):
        """
        Returns the player that has played the most matches.
        """
        return Player.objects.annotate(match_count=Count('matches')).order_by('-match_count').first()

    def can_join(self, match):
        """
        Check if the player can join the given match.
        A player can join a match if he has not joined already, and if the match
        has not been played already.
        """
        return (not match.players.filter(id=self.id).exists()) and (match.date > datetime.now())

    def can_leave(self, match):
        """
        Check if the player can leave the given match.
        A player can leave a match if he has joined and the match has not been
        played already.
        """
        return (match.players.filter(id=self.id).exists()) and (match.date > datetime.now())

    def create_user(self):
        """
        Create an user for the player.
        The username is automatically generated from the player's email, or random if needed.
        Return None if the player doesn't have a valid email.
        """
        # try to use first part of the email as the username
        username = self.email.partition('@')[0]
        # randomize username if needed
        if len(username) == 0 or len(username) > 30 or User.objects.filter(username=username).exists():
            username = str(datetime.now().timestamp())
        # create user
        return User.objects.create_user(username)

    def save(self, *args, **kwargs):
        # create user if needed
        if self.user == None:
            self.user = self.create_user()
            # TODO: send welcome email
        # save player
        super(Player, self).save(*args, **kwargs)


class Match(models.Model):
    """
    Model class representing a match.
    A match has basic information like date and place, and a list of players.
    Date is required and unique, and place is required.
    """

    date = models.DateTimeField(unique=True, db_index=True)
    place = models.CharField(max_length=50)
    players = models.ManyToManyField('Player', through='MatchPlayer')

    def __str__(self):
        return str(self.date)

    @classmethod
    def next_match(cls, date):
        """
        Return the first match after the given date.
        """
        return Match.objects.filter(date__gt=date).order_by('date').first()

    def player_count(self):
        """
        Returns the total number of players in the match, including guests.
        """
        return self.players.count() + self.guests.count()


class MatchPlayer(models.Model):
    """
    Model class representing the many-to-many relationship between matches and players.
    It has a join_date to store the date that the player joined the match.
    A player can join a match only once.
    """

    match = models.ForeignKey(Match)
    player = models.ForeignKey(Player)
    join_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['match', 'player']

    def __str__(self):
        return '%s joined %s on %s' % (self.player, self.match, self.join_date)


class Guest(models.Model):
    """
    Model class representing a guest in a match.
    Guests are external players that are invited to a match by a regular player.
    """

    name = models.CharField(max_length=50)
    match = models.ForeignKey(Match, related_name='guests')
    inviting_player = models.ForeignKey(Player)
    inviting_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['match', 'inviting_player', 'name']

    def __str__(self):
        return self.name


class WeeklyMatchSchedule(models.Model):
    """
    Model class representing a weekly match schedule for a given weekday, time
    and place.
    New Match instances will be automatically created every week according to
    the existing WeeklyMatchSchedule instances.
    """

    WEEKDAY_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    weekday = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(6)],
        choices=WEEKDAY_CHOICES)
    """
    Weekday as defined in datetime.weekday(): Monday is 0 and Sunday is 6.
    https://docs.python.org/2/library/datetime.html#datetime.datetime.weekday
    """

    time = models.TimeField()
    place = models.CharField(max_length=50)

    def __str__(self):
        date = self.next_datetime(datetime.now())
        date_str = date.strftime('%A %H:%M')
        return '{date}, {place}'.format(date=date_str, place=self.place)

    def find_next_match(self, date):
        """
        Find the next match after the given date that corresponds to this schedule.
        Returns None if not found.
        """
        next_datetime = self.next_datetime(date)
        match = Match.objects.filter(date=next_datetime).order_by('date').first()
        return match

    def create_next_match(self, date):
        """
        Create a match for the first date after the given date that corresponds
        to this schedule.
        """
        next_datetime = self.next_datetime(date)
        return Match.objects.create(date=next_datetime, place=self.place)

    def next_datetime(self, date):
        """
        Return the first date corresponding to the this weekly match schedule's
        weekday and time, after the given date.
        """
        date = datehelper.next_date(date=date, weekday=self.weekday)
        return datehelper.set_time(date=date, time=self.time)

    @classmethod
    def next_schedule(cls, date):
        """
        Return the next weekly match schedule from the given date.
        """
        query = Q(weekday__gt=date.weekday()) | (Q(weekday=date.weekday()) & Q(time__gt=date.time()))
        schedule = WeeklyMatchSchedule.objects.filter(query).order_by('weekday').first()

        if schedule == None:
            # check next week if needed
            schedule = WeeklyMatchSchedule.objects.order_by('weekday').first()

        return schedule
