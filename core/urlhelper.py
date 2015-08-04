"""
This module has helper functions for dealing with urls.
"""

from urllib.parse import urljoin
from django.core.urlresolvers import reverse
from django.conf import settings


def absolute_url(relative_url):
    """
    Absolute URL for `relative_url`, using `BASE_URL` defined in settings
    """
    return urljoin(settings.BASE_URL, relative_url)


def join_match_url(match, player):
    """
    Relative URL for `player` to join `match`
    """
    return reverse('join_match', args=[match.id, player.id])


def leave_match_url(match, player):
    """
    Relative URL for `player` to leave `match`
    """
    return reverse('leave_match', args=[match.id, player.id])


def match_url(match, player = None):
    """
    Relative URL for the given match and the given player.
    """
    url = reverse('match', args=[match.id])
    if player != None:
        url += '?player_id=%s' % player.id # TODO: kind of hacky
    return url
