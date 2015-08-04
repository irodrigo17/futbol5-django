"""
RESTful API module.
"""

from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, routers
from core.models import Player, Match, MatchPlayer, Guest, WeeklyMatchSchedule


# Serializers define the API representation.

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for the User model.
    """
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'email')


class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for the Player model.
    """
    class Meta:
        model = Player
        fields = ('url', 'id', 'name', 'email')


class GuestSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for the Guest model.
    """
    match = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='match-detail'
    )
    inviting_player = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='player-detail'
    )
    class Meta:
        model = Guest
        fields = ('url', 'id', 'name', 'inviting_date', 'match', 'inviting_player')


class MatchSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for the Match model.
    """
    players = PlayerSerializer(many=True, read_only=True)
    guests = GuestSerializer(many=True, read_only=True)
    class Meta:
        model = Match
        fields = ('url', 'id', 'date', 'place', 'players', 'guests')


class MatchPlayerSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for the MatchPlayer model.
    """
    match = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='match-detail'
    )
    player = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='player-detail'
    )
    class Meta:
        model = MatchPlayer
        fields = ('url', 'id', 'match', 'player')


class WeeklyMatchScheduleSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for the WeeklyMatchSchedule model.
    """
    class Meta:
        model = WeeklyMatchSchedule
        fields = ('url', 'id', 'weekday', 'time', 'place', 'invite_weekday')


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


class WeeklyMatchScheduleViewSet(viewsets.ModelViewSet):
    """
    View set class for the WeeklyMatchSchedule model.
    """
    queryset = WeeklyMatchSchedule.objects.all()
    serializer_class = WeeklyMatchScheduleSerializer


# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'matchplayers', MatchPlayerViewSet)
router.register(r'guests', GuestViewSet)
router.register(r'schedules', WeeklyMatchScheduleViewSet)
