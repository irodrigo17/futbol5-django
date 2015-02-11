from django.contrib import admin
from core.models import Player, Match, MatchPlayer

admin.site.register(Player)
admin.site.register(Match)
admin.site.register(MatchPlayer)
