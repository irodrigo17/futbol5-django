from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.conf import settings
from urlparse import urljoin
from core.models import Player, Match, MatchPlayer


def absolute_url(relative_url):
    return urljoin(settings.BASE_URL, relative_url)


def join_match_url(match, player):
    return absolute_url(reverse('core:join_match', args=[match.id, player.id]))


def leave_match_url(match, player):
    return absolute_url(reverse('core:leave_match', args=[match.id, player.id]))


def email_template_context(match, player):
    return Context({
        'player': player,
        'match': match,
        'join_match_url': join_match_url(match, player),
        'leave_match_url': leave_match_url(match, player),
    })


def render_content(template_path, match, player):
    template = get_template(template_path)
    context = email_template_context(match, player)
    return template.render(context)


def text_content(match, player):
    return render_content('core/join_match_email.txt', match, player)


def html_content(match, player):
    return render_content('core/join_match_email.html', match, player)


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
