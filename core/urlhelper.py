from urllib.parse import urljoin
from django.core.urlresolvers import reverse
from django.conf import settings
from core.models import Match, Player


def absolute_url(relative_url):
    """
    Absolute URL for `relative_url`, using `BASE_URL` defined in settings
    """
    return urljoin(settings.BASE_URL, relative_url)


def join_match_url(match, player):
    """
    Relative URL for `player` to join `match`
    """
    return reverse('core:join_match', args=[match.id, player.id])


def leave_match_url(match, player):
    """
    Relative URL for `player` to leave `match`
    """
    return reverse('core:leave_match', args=[match.id, player.id])


def match_url(match, player):
    url = reverse('core:match', args=[match.id])
    url += '?player=%s' % player.id # TODO: kind of hacky
    return url
