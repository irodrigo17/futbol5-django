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


class MatchPlayer(models.Model):

    match = models.ForeignKey(Match)
    player = models.ForeignKey(Player)
    join_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['match', 'player']

    def __str__(self):
        return str(self.player) + ' joined ' + str(self.match) + ' on ' + str(self.join_date)
