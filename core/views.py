"""
Django views module.
"""

import logging
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from core.models import Match, Player, MatchPlayer, Guest
from core import mailer, tasks
from core.urlhelper import match_url, join_match_url, leave_match_url


LOGGER = logging.getLogger(__name__)


# TODO: use generic views?


def current_player(request):
    """
    Get current player for the request.
    If player_id in GET parameters then set player_id in session,
    else try to get player_id from session.
    Return player with id = player_id, or None.
    """
    if 'player_id' in request.GET:
        request.session['player_id'] = int(request.GET['player_id'])

    if 'player_id' in request.session:
        try:
            return Player.objects.get(id=request.session['player_id'])
        except Player.DoesNotExist:
            LOGGER.info('Player does not exist, removing from session: %s' % request.session['player_id'])
            del request.session['player_id']
    else:
        return None


def set_current_player(request, context):
    """
    Get the current player from the request and set it to the context if available.
    """
    player = current_player(request)
    if player != None:
        context['player'] = player


def index(request):
    """
    View for the index page of the site.
    """
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    context = {
        'match_count': Match.objects.count(),
        'player_count': Player.objects.count(),
        'top_player': Player.top_player(),
        'next_match': Match.next_match(),
    }

    set_current_player(request, context)

    return render(request, 'core/index.html', context)


def match(request, match_id):
    """
    View for displaying a match with the given match_id.
    If the match does not exist returns 404.
    Any player stored in the session is set to the context.
    """
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    match = get_object_or_404(Match, pk=match_id)
    context = {'match': match}

    set_current_player(request, context)

    player = context.get('player', None)
    if player != None:
        context['can_join'] = player.can_join(match)
        context['join_match_url'] = join_match_url(match, player)
        context['leave_match_url'] = leave_match_url(match, player)

    return render(request, 'core/match.html', context)


def join_match(request, match_id, player_id):
    """
    View for joining a match.
    Adds the player with the given player_id to the match with the given
    match_id, and redirects to the match view upon success.
    If match or player do not exist it returns 404.
    If match has already been played returns 400.
    If player was already in the match it does nothing.
    Emails are sent to the match players.
    """
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    # TODO: should probably be POST to /matchplayers/ to be more RESTful,
    # but this get is way more email-friendly :)
    match = get_object_or_404(Match, pk=match_id)

    if datetime.now() >= match.date:
        # TODO: add proper HTML error page with a link to the next match
        # TODO: use model signals and keep validation in one place
        return HttpResponse(status=400, content='El partido ya fue')

    player = get_object_or_404(Player, pk=player_id)

    if not MatchPlayer.objects.filter(match=match, player=player).exists():
        match_player = MatchPlayer(match=match, player=player)
        match_player.save()
        sent_mails = mailer.send_join_mails(match, player)
        LOGGER.info('%s joined %s, sent %i email(s)' % (player, match, sent_mails))

    messages.success(request, '%s: Estás anotado para el partido!' % player.name)

    # TODO: add success/error/already-joined messages and player id
    return HttpResponseRedirect(match_url(match, player))


def leave_match(request, match_id, player_id):
    """
    View for leaving a match.
    Removes the player with the given player_id from the match with the given
    match_id, and redirects to the match view upon success.
    If match or player do not exist it returns 404.
    If match has already been played returns 400.
    If player had not joined the match, nothing happens.
    Emails are sent to the match players.
    """
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    # TODO: should probably be DELETE to /matchplayers/<id>/ to be more RESTful,
    # but this get is way more email-friendly :)
    match = get_object_or_404(Match, pk=match_id)

    if datetime.now() >= match.date:
        # TODO: add proper HTML error page with a link to the next match
        # TODO: use model signals and keep validation in one place
        return HttpResponse(status=400, content='El partido ya fue')

    player = get_object_or_404(Player, pk=player_id)

    mp = match.matchplayer_set.filter(player=player)
    if len(mp) > 0:
        mp.delete()
        # TODO: send emails asyncronously
        sent_mails = mailer.send_leave_mails(match, player)
        LOGGER.info('%s left %s, sent %i email(s)' % (player, match, sent_mails))

    messages.success(request, '%s: Te bajaste del partido, gracias por avisar!' % player.name)

    # TODO: add success/error/not-joined message and player id
    return HttpResponseRedirect(match_url(match, player))


def add_guest(request, match_id):
    """
    View for adding a guest.
    Adds a guest to the match with the given match_id, and redirects to the match.
    Expects the guest data in the POST.
    Returns 404 if the match or the inviting_player can't be foud.
    Returns 400 if the match has already been played.
    Emails are sent to the match players.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # TODO: should probably be a POST to /guests/ to be more RESTful
    match = get_object_or_404(Match, pk=match_id)

    if datetime.now() >= match.date:
        # TODO: add proper HTML error page with a link to the next match
        # TODO: use model signals and keep validation in one place
        return HttpResponse(status=400, content='El partido ya fue')

    player = get_object_or_404(Player, pk=request.POST['inviting_player'])

    guest = match.guests.create(inviting_player=player, name=request.POST['guest'])
    # TODO: send emails asyncronously
    sent_mails = mailer.send_invite_guest_mails(match, player, guest)
    LOGGER.info('%s invited %s to %s, sent %i email(s)' % (player, guest, match, sent_mails))

    messages.success(request, '%s: Tu amigo quedó anotado!' % player.name)

    # TODO: add success/error/not-joined message and player id
    return HttpResponseRedirect(match_url(match, player))


def remove_guest(request, guest_id):
    """
    View for removing a guest from a match.
    Removes the given guest from the match, and redirects to the match url.
    Returns 404 if the match or the guest can't be foud.
    Returns 400 if match has already been played.
    Emails are sent to the match players.
    """
    # TODO: should be a RESTful delete
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    guest = get_object_or_404(Guest, pk=guest_id)

    if datetime.now() >= guest.match.date:
        # TODO: add proper HTML error page with a link to the next match
        # TODO: use model signals and keep validation in one place
        return HttpResponse(status=400, content='El partido ya fue')

    guest.delete()

    sent_mails = mailer.send_remove_guest_mails(guest)
    LOGGER.info('%s uninvited %s from %s, sent %i email(s)' % (guest.inviting_player, guest, guest.match, sent_mails))

    messages.success(request, '%s: Tu amigo no juega, gracias por avisar!' % guest.inviting_player.name)

    # TODO: add success/error/not-joined message and player id
    return HttpResponseRedirect(match_url(guest.match, None))


@csrf_exempt
def send_mail(request):
    """
    View for sending emails.
    This view is hit daily by the scheduler to create matches when needed,
    and send email notifications to players.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    match = tasks.create_match_or_send_status(datetime.now())

    if match != None:
        return HttpResponse(status=201)
    else:
        return HttpResponse(status=204)
