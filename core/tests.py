from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from datetime import datetime

from core.models import Player, Match, MatchPlayer

# Model tests

class PlayerTests(TestCase):

    def test_name_is_unique(self):
        """
        name should be unique
        """
        p1 = Player(name='John', email='john@email.com')
        p1.full_clean()
        p1.save()

        p2 = Player(name='John', email='john2@email.com')
        with self.assertRaises(ValidationError):
            p2.full_clean()

    def test_email_is_unique(self):
        """
        email should be unique
        """
        p1 = Player(name='Jhon Smith', email='john@email.com')
        p1.full_clean()
        p1.save()

        p2 = Player(name='John Adams', email='john@email.com')
        with self.assertRaises(ValidationError):
            p2.full_clean()

    def test_name_is_not_blank(self):
        """
        name should not be blank
        """
        p = Player(name='', email='john@email.com')
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_email_is_not_blank(self):
        """
        email should not be blank
        """
        p = Player(name='John', email='')
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_email_is_valid(self):
        """
        email should have the correct format
        """
        p = Player(name='John', email='john.com')
        with self.assertRaises(ValidationError):
            p.full_clean()


class MatchTests(TestCase):

    def test_date_is_unique(self):
        """
        date should be unique
        """
        m1 = Match(date=datetime.now(), place='Maracana')
        m1.full_clean()
        m1.save()

        m2 = Match(date=m1.date, place='Maracana')
        with self.assertRaises(ValidationError):
            m2.full_clean()

    def test_date_is_not_blank(self):
        """
        date should not be blank
        """
        m = Match(place='Maracana')
        with self.assertRaises(ValidationError):
            m.full_clean()

    def test_place_is_not_blank(self):
        """
        place should not be blank
        """
        m = Match(date=datetime.now())
        with self.assertRaises(ValidationError):
            m.full_clean()


# View tests

class ViewTests(TestCase):

    def setUp(self):
        player = Player.objects.create(name='Test Player', email='test@player.com')
        match = Match.objects.create(date=datetime.now(), place='Test Stadium')

    def test_index_view(self):
        """
        index view should be rendered with the proper context and template
        """
        c = Client()
        response = c.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['player_count'], Player.objects.count())
        self.assertEquals(response.context['match_count'], Match.objects.count())
        self.assertEquals(len(response.templates), 1)
        self.assertEquals(response.templates[0].name, 'core/index.html')

    def test_match_view(self):
        """
        match view should be rendered with the proper context and template
        """
        c = Client()
        match = Match.objects.first()
        response = c.get('/matches/%d/' % match.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['match'], match)
        self.assertEquals(len(response.templates), 1)
        self.assertEquals(response.templates[0].name, 'core/match.html')

    def test_match_view_404(self):
        """
        match view should return a 404 if a match with the given id does not exist
        """
        c = Client()
        response = c.get('/matches/1234/')
        self.assertEquals(response.status_code, 404)

    def test_join_match_view(self):
        """
        join match view should redirect to match view and create the proper MatchPlayer
        """
        match = Match.objects.first()
        player = Player.objects.first()

        c = Client()
        response = c.get('/matches/%d/join/%d/' % (match.id, player.id), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['match'], match)
        self.assertEquals(len(response.templates), 1)
        self.assertEquals(response.templates[0].name, 'core/match.html')

        match_player = MatchPlayer.objects.get(match=match, player=player)
        self.assertEquals(match_player.match, match)
        self.assertEquals(match_player.player, player)

    def test_join_match_view_404(self):
        """
        join match view should return 404 if match or player do not exist
        """
        match = Match.objects.first()
        player = Player.objects.first()

        c = Client()
        response = c.get('/matches/%d/join/1234/' % match.id)
        self.assertEquals(response.status_code, 404)

        response = c.get('/matches/1234/join/%d/' % player.id)
        self.assertEquals(response.status_code, 404)

    def test_join_match_view_duplicate(self):
        """
        join match view should redirect to match view without creating any
        MatchPlayer if it already exists, and set a proper message in the context
        """
        match = Match.objects.first()
        player = Player.objects.first()

        c = Client()
        response = c.get('/matches/%d/join/%d/' % (match.id, player.id), follow=True)
        self.assertEquals(response.status_code, 200)

        match_player = MatchPlayer.objects.get(match=match, player=player)
        self.assertEquals(match_player.match, match)
        self.assertEquals(match_player.player, player)

        response = c.get('/matches/%d/join/%d/' % (match.id, player.id), follow=True)
        self.assertEquals(response.status_code, 200)

        match_player = MatchPlayer.objects.get(match=match, player=player)
        self.assertEquals(match_player.match, match)
        self.assertEquals(match_player.player, player)

    def test_leave_match_view(self):
        """
        leave match view should redirect to match view and delete the proper MatchPlayer
        """
        match = Match.objects.first()
        player = Player.objects.first()
        match_player = MatchPlayer.objects.create(match=match, player=player)

        c = Client()
        response = c.get('/matches/%d/leave/%d/' % (match.id, player.id), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['match'], match)
        self.assertEquals(len(response.templates), 1)
        self.assertEquals(response.templates[0].name, 'core/match.html')

        self.assertFalse(MatchPlayer.objects.filter(match=match, player=player).exists())

    def test_leave_match_view_404(self):
        """
        join match view should return 404 if match or player do not exist
        """
        match = Match.objects.first()
        player = Player.objects.first()

        c = Client()
        response = c.get('/matches/%d/leave/1234/' % match.id)
        self.assertEquals(response.status_code, 404)

        response = c.get('/matches/1234/leave/%d/' % player.id)
        self.assertEquals(response.status_code, 404)

        MatchPlayer.objects.all().delete()
        response = c.get('/matches/%d/join/%d/' % (match.id, player.id))
        self.assertEquals(response.status_code, 302)