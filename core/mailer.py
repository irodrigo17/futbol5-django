from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.core.exceptions import ObjectDoesNotExist
from core.models import Player, Match, MatchPlayer


def text_content(match, player):
    template = get_template('core/join_match_email.txt')
    context = Context({
        'player': player,
        'match': match,
    })
    return template.render(context)


def html_content(match, player):
    # TODO: DRY template rendering
    template = get_template('core/join_match_email.html')
    context = Context({
        'player': player,
        'match': match,
    })
    return template.render(context)


def email_address(player):
    return '%s <%s>' % (player.name, player.email)


def email_message(match, player):
    text = text_content(match, player)
    html = html_content(match, player)
    address = email_address(player)
    msg = EmailMultiAlternatives('Fobal', text, 'Fobal <noreply@fobal.com>', [address])
    msg.attach_alternative(html, "text/html")
    return msg


def send_invite_mail(match, player):
    email_message(match, player).send()


def send_invite_mails(matches, players):
    """
    Send emails to invite the given players to the given matches.
    """
    for player in players:
        for match in matches:
            send_invite_mail(match, player)


def test_mail():
    # TODO: remove me, only for debugging purposes
    player = Player()
    try:
        player = Player.objects.get(email='irodrigo17@gmail.com')
    except ObjectDoesNotExist:
        player = Player.objects.create(name="Ignacio Rodrigo", email='irodrigo17@gmail.com')
    match = Match.objects.create(date=datetime.now(), place='River')
    send_invite_mail(match, player)
