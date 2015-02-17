import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from core.models import Match, Player, MatchPlayer
from core import mailer, tasks

logger = logging.getLogger(__name__)

# TODO: use generic views?

def index(request):
    match_count = Match.objects.count()
    player_count = Player.objects.count()
    top_player = Player.top_player()
    context = {
        'match_count': match_count,
        'player_count': player_count,
        'top_player': top_player,
    }
    return render(request, 'core/index.html', context)


def match(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    context = {'match': match}
    return render(request, 'core/match.html', context)


def join_match(request, match_id, player_id):
    # TODO: should probably be POST to /matchplayers/ to be more RESTful,
    # but this get is way more email-friendly :)
    match = get_object_or_404(Match, pk=match_id)
    player = get_object_or_404(Player, pk=player_id)

    if not MatchPlayer.objects.filter(match=match, player=player).exists():
        match_player = MatchPlayer(match=match, player=player)
        match_player.save()
        mailer.send_join_mails(match, player)


    # TODO: add success/error/already-joined messages
    return HttpResponseRedirect(reverse('core:match', args=(match.id,)))


def leave_match(request, match_id, player_id):
    # TODO: should probably be DELETE to /matchplayers/<id>/ to be more RESTful,
    # but this get is way more email-friendly :)
    match = get_object_or_404(Match, pk=match_id)
    player = get_object_or_404(Player, pk=player_id)

    mp = match.matchplayer_set.filter(player=player)
    if len(mp) > 0:
        mp.delete()
        # TODO: send emails asyncronously
        mailer.send_leave_mails(match, player)

    # TODO: add success/error/not-joined message
    return HttpResponseRedirect(reverse('core:match', args=(match.id,)))


def send_mail(request):
    # TODO: should be a POST and secured
    sent_emails = 0
    if 'match' in request.GET and 'player' in request.GET:
        match = get_object_or_404(Match, pk=request.GET['match'])
        player = get_object_or_404(Player, pk=request.GET['player'])
        mailer.invite_message(match, player).send() # just for debugging
        sent_emails = 1
        logger.info('sending manual invite email to %s', player.email)
    else:
        sent_emails = tasks.create_matches_and_email_players()

    return HttpResponse('Emails sent: %i' % sent_emails)
