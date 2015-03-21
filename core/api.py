"""
RESTful API module.
"""

from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, routers
from core.models import Player, Match, MatchPlayer, Guest


# Serializers define the API representation.

# TODO: Add URLs to the serializers

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer class for the User model.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff')


class PlayerSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Player model.
    """
    class Meta:
        model = Player
        fields = ('id', 'name', 'email')


class MatchSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Match model.
    """
    class Meta:
        model = Match
        fields = ('id', 'date', 'place', 'players', 'guests')


class MatchPlayerSerializer(serializers.ModelSerializer):
    """
    Serializer class for the MatchPlayer model.
    """
    class Meta:
        model = MatchPlayer
        fields = ('id', 'match', 'player')


class GuestSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Guest model.
    """
    class Meta:
        model = Guest
        fields = ('id', 'name', 'match', 'inviting_player', 'inviting_date')


# ViewSets define the view behavior.

class UserViewSet(viewsets.ModelViewSet):
    """
    View set class for the User model.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    """
    View set class for the Player model.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class MatchViewSet(viewsets.ModelViewSet):
    """
    View set class for the Match model.
    """
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class MatchPlayerViewSet(viewsets.ModelViewSet):
    """
    View set class for the MatchPlayer model.
    """
    queryset = MatchPlayer.objects.all()
    serializer_class = MatchPlayerSerializer


class GuestViewSet(viewsets.ModelViewSet):
    """
    View set class for the Guest model.
    """
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'matchplayers', MatchPlayerViewSet)
router.register(r'guests', GuestViewSet)
