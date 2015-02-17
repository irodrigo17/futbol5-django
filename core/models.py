from datetime import datetime
from django.db import models
from django.core.validators import validate_email
from django.db.models import Count


class Player(models.Model):

    name = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=50, unique=True, db_index=True, validators=[validate_email])
    matches = models.ManyToManyField('Match', through='MatchPlayer')

    def __str__(self):
        return self.name

    @classmethod
    def top_player(cls):
        return Player.objects.annotate(match_count=Count('matches')).order_by('-match_count').first()


class Match(models.Model):

    date = models.DateTimeField(unique=True, db_index=True)
    place = models.CharField(max_length=50)
    players = models.ManyToManyField('Player', through='MatchPlayer')

    def __str__(self):
        return str(self.date)

    @classmethod
    def next_match(cls):
        return Match.objects.filter(date__gte=datetime.now()).order_by('date').first()


class MatchPlayer(models.Model):

    match = models.ForeignKey(Match)
    player = models.ForeignKey(Player)
    join_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['match', 'player']

    def __str__(self):
        return '%s joined %s on %s' % (self.player, self.match, self.join_date)


class Guest(models.Model):

    name = models.CharField(max_length=50)
    match = models.ForeignKey(Match, related_name='guests')
    inviting_player = models.ForeignKey(Player)
    inviting_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['match', 'inviting_player', 'name']

    def __str__(self):
        return self.name
