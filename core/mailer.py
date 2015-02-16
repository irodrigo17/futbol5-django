from datetime import datetime
from urllib.parse import urljoin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.conf import settings
from core.models import Player, Match, MatchPlayer


def absolute_url(relative_url):
    return urljoin(settings.BASE_URL, relative_url)


def join_match_url(match, player):
    return absolute_url(reverse('core:join_match', args=[match.id, player.id]))


def leave_match_url(match, player):
    return absolute_url(reverse('core:leave_match', args=[match.id, player.id]))


def match_url(match):
    return absolute_url(reverse('core:match', args=[match.id]))


def email_address(player):
    return '%s <%s>' % (player.name, player.email)


def join_match_message(match, player):
    context = Context({
        'player': player,
        'match': match,
        'join_match_url': join_match_url(match, player),
        'leave_match_url': leave_match_url(match, player),
    })

    text = get_template('core/join_match_email.txt').render(context)
    html = get_template('core/join_match_email.html').render(context)

    address = email_address(player)
    msg = EmailMultiAlternatives('Fobal', text, 'Fobal <noreply@fobal.com>', [address])
    msg.attach_alternative(html, "text/html")
    return msg


def send_invite_mails(matches, players):
    """
    Send emails to invite the given players to the given matches.
    """
    for player in players:
        for match in matches:
            join_match_message(match, player).send()


def leave_match_message(match, player, leaving_player):
    context = Context({
        'player': player,
        'leaving_player': leaving_player,
        'match': match,
        'match_url': match_url(match),
    })

    text = get_template('core/leave_match_email.txt').render(context)
    html = get_template('core/leave_match_email.html').render(context)

    address = email_address(player)
    msg = EmailMultiAlternatives('Fobal', text, 'Fobal <noreply@fobal.com>', [address])
    msg.attach_alternative(html, "text/html")
    return msg


def send_leave_mails(match, leaving_player):
    """
    Send email notifications to all players in the given match to inform that
    the given leaving_player is not playing.
    leaving_player should have been removing from match.players already.
    """
    for player in match.players.all():
        leave_match_message(match, player, leaving_player).send()
