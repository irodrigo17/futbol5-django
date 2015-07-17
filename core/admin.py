"""
Django admin configuration.
"""

from django.contrib import admin
from core.models import Player, Match, MatchPlayer, Guest, WeeklyMatchSchedule

admin.site.register(Player)
admin.site.register(Match)
admin.site.register(MatchPlayer)
admin.site.register(Guest)
admin.site.register(WeeklyMatchSchedule)
