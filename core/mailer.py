"""
Mailer module for sending emails.
"""

from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from core.urlhelper import absolute_url, join_match_url, leave_match_url, match_url
import threading
import logging


LOGGER = logging.getLogger(__name__)


class EmailThread(threading.Thread):
    """
    Thread subclass for sending email asynchronously.
    """

    def __init__(self, messages):
        self.messages = messages
        threading.Thread.__init__(self)

    def run (self):
        get_connection().send_messages(self.messages)
        LOGGER.info('Sent %i emails in background' % len(self.messages))


def send_mails(messages, async=True):
    """
    Sends the given email messages using the default email backend.
    The operation is asynchronous by default.
    """
    if async == True:
        EmailThread(messages).start()
    else:
        get_connection().send_messages(messages)


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


def send_invite_mails(match, players, async=True):
    """
    Send emails to invite the given players to the given match.
    This is a convenience method that uses invite_message to create and send
    messages for all players.
    Returns the number of emails sent.
    """
    messages = []
    for player in players:
        messages.append(invite_message(match, player))
    send_mails(messages, async)
    return len(messages)


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


def send_leave_mails(match, leaving_player, async=True):
    """
    Send email notifications to all players in the given match to inform that
    the given leaving_player is not playing.
    This is a convenience method that uses leave_match_message to create messages.
    Returns the number of emails sent.
    """
    messages = []
    for player in match.players.all():
        if player != leaving_player:
            messages.append(leave_match_message(match, player, leaving_player))
    send_mails(messages, async)
    return len(messages)


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


def send_join_mails(match, joining_player, async=True):
    """
    Send email notifications to all players in the given match to inform that
    the given joining_player has joined.
    This is a convenience method that uses join_match_message and returns the
    number of emails sent.
    """
    messages = []
    for player in match.players.all():
        if player != joining_player:
            messages.append(join_match_message(match, player, joining_player))
    send_mails(messages, async)
    return len(messages)


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


def send_invite_guest_mails(match, inviting_player, guest, async=True):
    """
    Send email notifications to all players but the inviting_player in the given
    match to inform that the given inviting_player has invited the given guest.
    Convenience method that calls invite_guest_message and returns the number of
    emails sent.
    """
    messages = []
    for player in match.players.all():
        if player != inviting_player:
            messages.append(invite_guest_message(match, player, inviting_player, guest))
    send_mails(messages, async)
    return len(messages)


def remove_guest_message(guest, player):
    """
    Creates and returns an email message to notify the given player about the
    inviting_player removing the guest from the match.
    Contains plain text and HTML versions of the body and a link to the match.
    """
    context = Context({
        'player': player,
        'match_url': absolute_url(match_url(guest.match, player)),
        'guest': guest,
    })

    text = get_template('core/remove_guest_email.txt').render(context)
    html = get_template('core/remove_guest_email.html').render(context)

    address = email_address(player)
    msg = EmailMultiAlternatives('Fobal', text, 'Fobal <noreply@fobal.com>', [address])
    msg.attach_alternative(html, "text/html")
    return msg


def send_remove_guest_mails(guest, async=True):
    """
    Send email notifications to all match players but the inviting_player in the given
    match to inform that the given guest has been removed from the match.
    Convenience method that calls remove_guest_message and returns the number of
    emails sent.
    """
    messages = []
    for player in guest.match.players.all():
        if player != guest.inviting_player:
            messages.append(remove_guest_message(guest, player))
    send_mails(messages, async)
    return len(messages)


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


def send_status_mails(match, players, async=True):
    """
    Send email notifications to all match players with the status of the match.
    Convenience method that calls status_mail and returns the number of
    emails sent.
    """
    messages = []
    for player in players:
        messages.append(status_message(match, player))
    send_mails(messages, async)
    return len(messages)
