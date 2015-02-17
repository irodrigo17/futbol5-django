from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.core.exceptions import ObjectDoesNotExist
from core.models import Player, Match, MatchPlayer
from core.urlhelper import absolute_url, join_match_url, leave_match_url, match_url

def email_address(player):
    return '%s <%s>' % (player.name, player.email)


def invite_message(match, player):
    context = Context({
        'player': player,
        'match': match,
        'join_match_url': absolute_url(join_match_url(match, player)),
        'leave_match_url': absolute_url(leave_match_url(match, player)),
    })

    text = get_template('core/match_invite_email.txt').render(context)
    html = get_template('core/match_invite_email.html').render(context)

    address = email_address(player)
    msg = EmailMultiAlternatives('Fobal', text, 'Fobal <noreply@fobal.com>', [address])
    msg.attach_alternative(html, "text/html")
    return msg


def send_invite_mails(matches, players):
    """
    Send emails to invite the given players to the given matches.
    """
    sent_mails = 0
    for player in players:
        for match in matches:
            invite_message(match, player).send()
            sent_mails += 1
    return sent_mails


def leave_match_message(match, player, leaving_player):
    context = Context({
        'player': player,
        'leaving_player': leaving_player,
        'match': match,
        'match_url': absolute_url(match_url(match, player)),
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
    sent_mails = 0
    for player in match.players.all():
        leave_match_message(match, player, leaving_player).send()
        sent_mails += 1
    return sent_mails

def join_match_message(match, player, joining_player):
    context = Context({
        'player': player,
        'joining_player': joining_player,
        'match': match,
        'match_url': absolute_url(match_url(match, player)),
    })

    text = get_template('core/join_match_email.txt').render(context)
    html = get_template('core/join_match_email.html').render(context)

    address = email_address(player)
    msg = EmailMultiAlternatives('Fobal', text, 'Fobal <noreply@fobal.com>', [address])
    msg.attach_alternative(html, "text/html")
    return msg


def send_join_mails(match, joining_player):
    """
    Send email notifications to all players in the given match to inform that
    the given joining_player has joined.
    joining_player should not be added to match.players yet.
    """
    sent_mails = 0
    for player in match.players.all():
        if player != joining_player:
            join_match_message(match, player, joining_player).send()
            sent_mails += 1
    return sent_mails


def invite_guest_message(match, player, inviting_player, guest):
    context = Context({
        'player': player,
        'inviting_player': inviting_player,
        'match': match,
        'match_url': absolute_url(match_url(match, player)),
        'guest': guest,
    })

    text = get_template('core/invite_guest_email.txt').render(context)
    html = get_template('core/invite_guest_email.html').render(context)

    address = email_address(player)
    msg = EmailMultiAlternatives('Fobal', text, 'Fobal <noreply@fobal.com>', [address])
    msg.attach_alternative(html, "text/html")
    return msg


def send_invite_guest_mails(match, inviting_player, guest):
    """
    Send email notifications to all players in the given match to inform that
    the given inviting_player has invited the given giest to play.
    """
    sent_mails = 0
    for player in match.players.all():
        if player != inviting_player:
            invite_guest_message(match, player, inviting_player, guest).send()
            sent_mails += 1
    return sent_mails
