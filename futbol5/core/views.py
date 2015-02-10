from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Futbol 5 / Index")

def match(request, match_id):
    return HttpResponse("Match: %s" % match_id)

def join_match(request, match_id, player_id):
    return HttpResponse("Join match: %s as player: %s" % (match_id, player_id))
