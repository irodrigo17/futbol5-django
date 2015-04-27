"""
Module for Django models.
"""

from datetime import datetime
from django.db import models
from django.core.validators import validate_email
from django.db.models import Count


class Player(models.Model):
    """
    Model class representing a player.
    A player has basic personal information like name and email.
    Name and email are required and unique.
    """

    name = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=50, unique=True, db_index=True, validators=[validate_email])
    matches = models.ManyToManyField('Match', through='MatchPlayer')

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
    def next_match(cls):
        """
        Return the next upcoming match.
        """
        return Match.objects.filter(date__gte=datetime.now()).order_by('date').first()

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
