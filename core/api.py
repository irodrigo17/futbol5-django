"""
RESTful API module.
"""

import logging
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, routers, permissions
from core.models import Player, Match, MatchPlayer, Guest, WeeklyMatchSchedule


LOGGER = logging.getLogger(__name__)


# Serializers define the API representation.


class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for the Player model.
    """
    class Meta:
        model = Player
        fields = ('url', 'id', 'name', 'email')

    def create(self, validated_data):
        player = Player.objects.create(**validated_data)
        player.user.set_password(self.initial_data['password'])
        return player


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


# Permissions control user access to the different resources


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Full permissions for admins, read only permissions for everybody.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Full permissions for owner or admin, read only permissions for everybody.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.owner == request.user or request.user.is_staff


class PlayerPermissions(permissions.BasePermission):
    """
    Custom permissions for the players endpoint.
    Posting a new player is public, getting players is for authenticated users
    only, and updating or deleting players is allowed only to the owner or admins.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        else:
            return request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated()
        else:
            return request.user.is_staff or obj.owner == request.user


# ViewSets define the view behavior.


class PlayerViewSet(viewsets.ModelViewSet):
    """
    View set class for the Player model.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [PlayerPermissions]


class MatchViewSet(viewsets.ModelViewSet):
    """
    View set class for the Match model.
    """
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class MatchPlayerViewSet(viewsets.ModelViewSet):
    """
    View set class for the MatchPlayer model.
    """
    queryset = MatchPlayer.objects.all()
    serializer_class = MatchPlayerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class GuestViewSet(viewsets.ModelViewSet):
    """
    View set class for the Guest model.
    """
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class WeeklyMatchScheduleViewSet(viewsets.ModelViewSet):
    """
    View set class for the WeeklyMatchSchedule model.
    """
    queryset = WeeklyMatchSchedule.objects.all()
    serializer_class = WeeklyMatchScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'matchplayers', MatchPlayerViewSet)
router.register(r'guests', GuestViewSet)
router.register(r'schedules', WeeklyMatchScheduleViewSet)
