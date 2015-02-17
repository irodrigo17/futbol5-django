import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from core.models import Match, Player, MatchPlayer
from core import mailer, tasks
from core.urlhelper import absolute_url, join_match_url, leave_match_url, match_url

logger = logging.getLogger(__name__)

# TODO: use generic views?

def index(request):
    context = {
        'match_count': Match.objects.count(),
        'player_count': Player.objects.count(),
        'top_player': Player.top_player(),
        'next_match': Match.next_match(),
    }
    return render(request, 'core/index.html', context)


def match(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    context = {'match': match}

    if 'player' in request.GET:
        context['player'] = get_object_or_404(Player, pk=request.GET['player'])

    return render(request, 'core/match.html', context)


def join_match(request, match_id, player_id):
    # TODO: should probably be POST to /matchplayers/ to be more RESTful,
    # but this get is way more email-friendly :)
    match = get_object_or_404(Match, pk=match_id)
    player = get_object_or_404(Player, pk=player_id)

    if not MatchPlayer.objects.filter(match=match, player=player).exists():
        match_player = MatchPlayer(match=match, player=player)
        match_player.save()
        sent_mails = mailer.send_join_mails(match, player)
        logger.info('%s joined %s, sent %i email(s)' % (player, match, sent_mails))

    # TODO: add success/error/already-joined messages and player id
    return HttpResponseRedirect(match_url(match, player))


def leave_match(request, match_id, player_id):
    # TODO: should probably be DELETE to /matchplayers/<id>/ to be more RESTful,
    # but this get is way more email-friendly :)
    match = get_object_or_404(Match, pk=match_id)
    player = get_object_or_404(Player, pk=player_id)

    mp = match.matchplayer_set.filter(player=player)
    if len(mp) > 0:
        mp.delete()
        # TODO: send emails asyncronously
        sent_mails = mailer.send_leave_mails(match, player)
        logger.info('%s left %s, sent %i email(s)' % (player, match, sent_mails))

    # TODO: add success/error/not-joined message and player id
    return HttpResponseRedirect(match_url(match, player))


def add_guest(request, match_id):
    # TODO: should probably be a POST to /guests/ to be more RESTful
    match = get_object_or_404(Match, pk=match_id)
    player = get_object_or_404(Player, pk=request.POST['inviting_player'])

    guest = match.guests.create(inviting_player=player, name=request.POST['guest'])
    # TODO: send emails asyncronously
    sent_mails = mailer.send_invite_guest_mails(match, player, guest)
    logger.info('%s invited %s to %s, sent %i email(s)' % (player, guest, match, sent_mails))

    # TODO: add success/error/not-joined message and player id
    return HttpResponseRedirect(match_url(match, player))


def send_mail(request):
    # TODO: should be a POST and secured
    sent_emails = 0
    if 'match' in request.GET and 'player' in request.GET:
        match = get_object_or_404(Match, pk=request.GET['match'])
        player = get_object_or_404(Player, pk=request.GET['player'])
        mailer.invite_message(match, player).send() # just for debugging
        sent_emails = 1
        logger.info('Sending manual invite email for %s to join %s' % (player, match))
    else:
        sent_emails = tasks.create_matches_and_email_players()
        logger.info('Created week matches and sent %i join email(s)' % (sent_emails))

    return HttpResponse('Emails sent: %i' % sent_emails)
