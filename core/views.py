from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from core.models import Match, Player, MatchPlayer
from core import mailer, tasks


# TODO: use generic views?

def index(request):
    match_count = Match.objects.count()
    player_count = Player.objects.count()
    # TODO: Add top players, players ranked by number of matches
    context = {'match_count': match_count, 'player_count': player_count}
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

    if MatchPlayer.objects.filter(match=match, player=player).exists() == False:
        match_player = MatchPlayer(match=match, player=player)
        match_player.save()

    # TODO: add success/error/already-joined messages
    return HttpResponseRedirect(reverse('core:match', args=(match.id,)))


def leave_match(request, match_id, player_id):
    # TODO: should probably be DELETE to /matchplayers/<id>/ to be more RESTful,
    # but this get is way more email-friendly :)
    match = get_object_or_404(Match, pk=match_id)
    player = get_object_or_404(Player, pk=player_id)
    match_player = get_object_or_404(MatchPlayer, match=match, player=player)
    match_player.delete()
    # TODO: add success message
    return HttpResponseRedirect(reverse('core:match', args=(match.id,)))


def send_mail(request):
    # TODO: should be a POST and secured
    tasks.create_matches_and_email_players()
    return HttpResponse(status=204)
