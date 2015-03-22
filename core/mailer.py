"""
Mailer module for sending emails.
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from core.urlhelper import absolute_url, join_match_url, leave_match_url, match_url


def email_address(player):
    """
    Email address for the given player.
    """
    return '%s <%s>' % (player.name, player.email)


def invite_message(match, player):
    """
    Email message for inviting the given player to the given match.
    Includes plain text and HTML versions of the body.
    Includes links for the player to join/leave the match,
    and a link to the match itself.
    """
    context = Context({
        'player': player,
        'match': match,
        'match_url': absolute_url(match_url(match, player)),
        'join_match_url': absolute_url(join_match_url(match, player)),
        'leave_match_url': absolute_url(leave_match_url(match, player)),
    })

    text = get_template('core/match_invite_email.txt').render(context)
    html = get_template('core/match_invite_email.html').render(context)

    address = email_address(player)
    msg = EmailMultiAlternatives('Fobal', text, 'Fobal <noreply@fobal.com>', [address])
    msg.attach_alternative(html, "text/html")
    return msg


def send_invite_mails(match, players):
    """
    Send emails to invite the given players to the given match.
    This is a convenience method that uses invite_message to create and send
    messages for all players.
    Returns the number of emails sent.
    """
    sent_mails = 0
    for player in players:
        invite_message(match, player).send()
        sent_mails += 1
    return sent_mails


def leave_match_message(match, player, leaving_player):
    """
    Email message to notify the given player about the leaving_player leaving the match.
    Includes plain text and HTML versions of the body.
    Includes a link to the match.
    """
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
    This is a convenience method that uses leave_match_message to create messages.
    Returns the number of emails sent.
    """
    sent_mails = 0
    for player in match.players.all():
        if player != leaving_player:
            leave_match_message(match, player, leaving_player).send()
            sent_mails += 1
    return sent_mails


def join_match_message(match, player, joining_player):
    """
    Creates and returns an email message to notify the given player about
    the given joining_player joining the given match.
    Includes plain text and HTML vesions of the body and a link to the match.
    """
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
    This is a convenience method that uses join_match_message and returns the
    number of emails sent.
    """
    sent_mails = 0
    for player in match.players.all():
        if player != joining_player:
            join_match_message(match, player, joining_player).send()
            sent_mails += 1
    return sent_mails


def invite_guest_message(match, player, inviting_player, guest):
    """
    Creates and returns an email message to notify the given player about the
    inviting_player inviting the guest to the match.
    Contains plain text and HTML versions of the body and a link to the match.
    """
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
    Send email notifications to all players but the inviting_player in the given
    match to inform that the given inviting_player has invited the given guest.
    Convenience method that calls invite_guest_message and returns the number of
    emails sent.
    """
    sent_mails = 0
    for player in match.players.all():
        if player != inviting_player:
            invite_guest_message(match, player, inviting_player, guest).send()
            sent_mails += 1
    return sent_mails


def status_message(match, player):
    """
    Creates and returns an email message for the given player with the status
    of the given match.
    Contains plain text and HTML versions in the body, and a link to the match.
    """
    context = Context({
        'player': player,
        'match': match,
        'match_url': absolute_url(match_url(match, player)),
    })

    text = get_template('core/status_email.txt').render(context)
    html = get_template('core/status_email.html').render(context)

    address = email_address(player)
    msg = EmailMultiAlternatives('Fobal', text, 'Fobal <noreply@fobal.com>', [address])
    msg.attach_alternative(html, "text/html")
    return msg


def send_status_mails(match):
    """
    Send email notifications to all match players with the status of the match.
    Convenience method that calls status_mail and returns the number of
    emails sent.
    """
    sent_mails = 0
    for player in match.players.all():
        status_message(match, player).send()
        sent_mails += 1
    return sent_mails
