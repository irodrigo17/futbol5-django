from django.db import models


class Player(models.Model):

    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)

    # TODO: add matches many-to-many relationship
    # TODO: validate name and email

    def __str__(self):
        return self.name


class Match(models.Model):

    date = models.DateTimeField()
    place = models.CharField(max_length=50)

    # TODO: add players many-to-many relationship
    # TODO: validate date and place

    def __str__(self):
        return str(self.date)


class MatchPlayer(models.Model):

    match = models.ForeignKey(Match)
    player = models.ForeignKey(Player)
    join_date = models.DateTimeField(auto_now_add=True)

    # TODO: validate match and player

    def __str__(self):
        return str(self.player) + ' joined ' + str(self.match) + ' on ' + str(self.join_date)
