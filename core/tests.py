"""
Tests module for the following modules:
- models
- views
- mailer
- tasks
- urlhelper
"""

from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import datetime, timedelta
from urllib.parse import urljoin
from django.core import mail

from core.models import Player, Match, MatchPlayer, Guest
from core import tasks, mailer
from core.urlhelper import absolute_url, join_match_url, leave_match_url, match_url

# Model tests

class PlayerTests(TestCase):
    """
    TestCase subclass for the Player model.
    """

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

    def test_top_player(self):
        """
        top_player should return the player with the most games played
        """
        p0 = Player.objects.create(name='0 matches', email='0matches@email.com')
        p1 = Player.objects.create(name='1 matches', email='1matches@email.com')
        p2 = Player.objects.create(name='2 matches', email='2matches@email.com')

        m0 = Match.objects.create(date=datetime.now(), place='Here')
        m1 = Match.objects.create(date=datetime.now(), place='Here')

        MatchPlayer.objects.create(player=p1, match=m0)
        MatchPlayer.objects.create(player=p2, match=m0)
        MatchPlayer.objects.create(player=p2, match=m1)

        top_player = Player.top_player()
        self.assertTrue(top_player, p2)


    def test_can_join(self):
        """
        can_join should be True iff player has not joined already
        and the match has not been played yet.
        """
        m1 = Match.objects.create(date=datetime.now() - timedelta(days=1))
        m2 = Match.objects.create(date=datetime.now() + timedelta(days=1))

        p1 = Player.objects.create(name='Player1', email="p1@email.com")
        p2 = Player.objects.create(name='Player2', email="p2@email.com")

        self.assertFalse(p1.can_join(m1))
        self.assertFalse(p2.can_join(m1))

        self.assertTrue(p1.can_join(m2))
        self.assertTrue(p2.can_join(m2))

        MatchPlayer.objects.create(match=m2, player=p1)
        self.assertFalse(p1.can_join(m2))
        self.assertTrue(p2.can_join(m2))


    def test_can_leave(self):
        """
        can_leave should be True iff player has joined already
        and the match has not been played yet.
        """
        past_match = Match.objects.create(date=datetime.now() - timedelta(days=1))
        future_match = Match.objects.create(date=datetime.now() + timedelta(days=1))

        p1 = Player.objects.create(name='Player1', email="p1@email.com")
        p2 = Player.objects.create(name='Player2', email="p2@email.com")

        self.assertFalse(p1.can_join(past_match))
        self.assertFalse(p2.can_join(past_match))

        self.assertTrue(p1.can_join(future_match))
        self.assertTrue(p2.can_join(future_match))

        MatchPlayer.objects.create(match=future_match, player=p1)
        self.assertFalse(p1.can_join(future_match))
        self.assertTrue(p2.can_join(future_match))


class MatchTests(TestCase):
    """
    TestCase subclass for the Match model.
    """

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

    def test_next_match(self):
        """
        next match should return the next updcoming match
        """
        m1 = Match.objects.create(date=datetime.now() - timedelta(days=1), place='Here')
        m2 = Match.objects.create(date=datetime.now() + timedelta(days=1), place='There')
        m3 = Match.objects.create(date=datetime.now() + timedelta(days=2), place='Everywhere')
        next_match = Match.next_match()
        self.assertTrue(next_match == m2)

        m4 = Match.objects.create(date=datetime.now() + timedelta(minutes=1), place='Really Close')
        next_match = Match.next_match()
        self.assertTrue(next_match == m4)


    def test_player_count(self):
        """
        player_count should return the total number of players in the match, including guests.
        """
        match = Match.objects.create(date=datetime.now(), place='Player Count')
        self.assertEquals(match.player_count(), 0)

        p1 = Player.objects.create(name='Player One', email='p1@email.com')
        match.matchplayer_set.create(player=p1)
        self.assertEquals(match.player_count(), 1)

        p2 = Player.objects.create(name='Player Two', email='p2@email.com')
        match.matchplayer_set.create(player=p2)
        self.assertEquals(match.player_count(), 2)

        match.guests.create(name='Guest', inviting_player=p1)
        self.assertEquals(match.player_count(), 3)


# View tests

class ViewTests(TestCase):
    """
    TestCase subclass for the views module.
    """

    def test_index_view(self):
        """
        Index view should be rendered with the proper context and template.
        """
        c = Client()
        response = c.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['player_count'], Player.objects.count())
        self.assertEquals(response.context['match_count'], Match.objects.count())
        self.assertEquals(response.context['top_player'], Player.top_player())
        self.assertEquals(response.context['next_match'], Match.next_match())
        self.assertEquals(response.templates[0].name, 'core/index.html')

        Match.objects.create(date=datetime.now() + timedelta(days=1), place='River')
        Player.objects.create(name="Johan Sebastian Mastropiero", email='js@mastropiero.com')

        response = c.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['player_count'], Player.objects.count())
        self.assertEquals(response.context['match_count'], Match.objects.count())
        self.assertEquals(response.context['top_player'], Player.top_player())
        self.assertEquals(response.context['next_match'], Match.next_match())


    def test_match_view(self):
        """
        Match view should be rendered with the proper context and template.
        """
        c = Client()
        match = Match.objects.create(date=datetime.now(), place="La Cancha")
        response = c.get('/matches/%d/' % match.id)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['match'], match)
        self.assertFalse('player' in response.context)
        self.assertEquals(response.templates[0].name, 'core/match.html')
        self.assertFalse("<form action=\"addguest/\" method=\"post\">" in str(response.content))
        self.assertFalse("Juego!" in str(response.content))
        self.assertFalse('join_match_url' in response.context)
        self.assertFalse('leave_match_url' in response.context)


    def test_match_view_with_valid_player(self):
        """
        Match view with a valid player should render properly.
        """
        c = Client()
        match = Match.objects.create(date=datetime.now() + timedelta(days=1), place="La Cancha")
        player = Player.objects.create(name='Test Match View', email="test@matchview.com")
        response = c.get('/matches/%d/' % match.id, {'player_id': player.id}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['match'], match)
        self.assertEquals(response.context['player'], player)
        self.assertEquals(response.templates[0].name, 'core/match.html')
        self.assertTrue("<form action=\"addguest/\" method=\"post\">" in str(response.content))
        self.assertTrue("Juego" in str(response.content))
        self.assertTrue('join_match_url' in response.context)
        self.assertFalse('leave_match_url' in response.context)


    def test_match_view_with_guest(self):
        """
        Player should be able to remove guests invited by himself.
        """
        c = Client()
        match = Match.objects.create(date=datetime.now() + timedelta(days=1), place="La Cancha")
        player1 = Player.objects.create(name='Test Match View 1', email="test1@matchview.com")
        player2 = Player.objects.create(name='Test Match View 2', email="test2@matchview.com")
        match.matchplayer_set.create(player=player1)
        match.matchplayer_set.create(player=player2)
        guest1 = Guest.objects.create(name='Guest1', inviting_player=player1, match=match)
        guest2 = Guest.objects.create(name='Guest2', inviting_player=player2, match=match)
        response = c.get('/matches/%d/' % match.id, {'player_id': player1.id}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['match'], match)
        self.assertEquals(response.context['player'], player1)
        self.assertEquals(response.templates[0].name, 'core/match.html')
        self.assertTrue("<form action=\"addguest/\" method=\"post\">" in str(response.content))
        self.assertTrue("No juego" in str(response.content))
        self.assertFalse('join_match_url' in response.context)
        self.assertTrue('leave_match_url' in response.context)
        self.assertTrue('removeguest/%i/' % guest1.id in str(response.content))
        self.assertFalse('removeguest/%i/' % guest2.id in str(response.content))


    def test_match_view_with_invalid_player(self):
        """
        Match view with an invalid player should render as if there were no player.
        """
        c = Client()
        match = Match.objects.create(date=datetime.now(), place="La Cancha")
        response = c.get('/matches/%d/' % match.id, {'player_id': 12345}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertFalse('player' in response.context)


    def test_match_view_404(self):
        """
        Match view should return a 404 if a match with the given id does not exist.
        """
        c = Client()
        response = c.get('/matches/1234/')
        self.assertEquals(response.status_code, 404)


    def test_join_match_view(self):
        """
        Join match view should redirect to match view and create the proper MatchPlayer.
        """
        match = Match.objects.create(date=datetime.now() + timedelta(days=2), place="Centenario")
        player = Player.objects.create(name="Join Match View", email="join@match.com")

        c = Client()
        response = c.get('/matches/%d/join/%d/' % (match.id, player.id), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['match'], match)
        self.assertEquals(response.templates[0].name, 'core/match.html')

        match_player = MatchPlayer.objects.get(match=match, player=player)
        self.assertEquals(match_player.match, match)
        self.assertEquals(match_player.player, player)


    def test_join_match_view_404(self):
        """
        Join match view should return 404 if match or player do not exist.
        """
        match = Match.objects.create(date=datetime.now() + timedelta(hours=2), place="Centenario")
        player = Player.objects.create(name="Join Match View 404", email="join404@match.com")

        c = Client()
        response = c.get('/matches/%d/join/1234/' % match.id)
        self.assertEquals(response.status_code, 404)

        response = c.get('/matches/1234/join/%d/' % player.id)
        self.assertEquals(response.status_code, 404)


    def test_join_match_view_duplicate(self):
        """
        Join match view should redirect to match view without creating any
        MatchPlayer if it already exists, and set a proper message in the context.
        """
        match = Match.objects.create(date=datetime.now() + timedelta(seconds=10), place="Centenario")
        player = Player.objects.create(name="Join Match View Duplicate", email="join@dup.com")

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


    def test_join_match_view_after(self):
        """
        Join match view should fail if current date > match date.
        """
        match = Match.objects.create(date=datetime.now() - timedelta(seconds=1), place="Centenario")
        player = Player.objects.create(name="Join Match View After", email="join@dup.com")

        c = Client()
        response = c.get('/matches/%d/join/%d/' % (match.id, player.id), follow=True)
        self.assertEquals(response.status_code, 400)


    def test_leave_match_view(self):
        """
        Leave match view should redirect to match view and delete the proper MatchPlayer.
        """
        match = Match.objects.create(date=datetime.now() + timedelta(days=2), place='Here')
        player1 = Player.objects.create(name='Leave Match 1', email='leavematch1@email.com')
        player2 = Player.objects.create(name='Leave Match 2', email='leavematch2@email.com')
        mp1 = MatchPlayer.objects.create(match=match, player=player1)
        mp2 = MatchPlayer.objects.create(match=match, player=player2)

        self.assertEquals(match.players.count(), 2)

        c = Client()
        response = c.get('/matches/%d/leave/%d/' % (match.id, player2.id), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['match'], match)
        self.assertEquals(len(mail.outbox), 1, 'Should send an email to the remaining player')
        self.assertFalse(MatchPlayer.objects.filter(match=match, player=player2).exists())
        self.assertTrue(MatchPlayer.objects.filter(match=match, player=player1).exists())

        mail.outbox = []
        response = c.get('/matches/%d/leave/%d/' % (match.id, player2.id), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 0, "Shouldn't send any email if player was not in the match")


    def test_leave_match_view_404(self):
        """
        Join match view should return 404 if match or player do not exist.
        """
        match = Match.objects.create(date=datetime.now() + timedelta(days=2), place="Centenario")
        player = Player.objects.create(name="Leave Match 404", email="leave404@match.com")

        c = Client()
        response = c.get('/matches/%d/leave/1234/' % match.id)
        self.assertEquals(response.status_code, 404)

        response = c.get('/matches/1234/leave/%d/' % player.id)
        self.assertEquals(response.status_code, 404)

        MatchPlayer.objects.all().delete()
        response = c.get('/matches/%d/join/%d/' % (match.id, player.id))
        self.assertEquals(response.status_code, 302)


    def test_leave_match_view_after(self):
        """
        Leave match view should fail if current date > match date.
        """
        match = Match.objects.create(date=datetime.now() - timedelta(seconds=1), place="Centenario")
        player = Player.objects.create(name="Leave Match View After", email="leave@after.com")

        c = Client()
        response = c.get('/matches/%d/leave/%d/' % (match.id, player.id), follow=True)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.status_code, 400)


    def test_add_guest(self):
        """
        Adding a guest should work as expected with correct data.
        """
        match = Match.objects.create(date=datetime.now() + timedelta(seconds=10), place='Somewhere')
        inviter = Player.objects.create(name='Inviter', email='inviter@email.com')
        other_player = Player.objects.create(name='Other Player', email='other@player.com')
        match.matchplayer_set.create(player=inviter)
        match.matchplayer_set.create(player=other_player)

        c = Client()
        post_data = {
            'inviting_player': inviter.id,
            'guest': 'Invitee',
        }
        response = c.post('/matches/%d/addguest/' % match.id, post_data, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['match'], match)
        self.assertEquals(response.context['player'], inviter)
        self.assertEquals(response.templates[0].name, 'core/match.html')

        guest = Guest.objects.get(match=match, inviting_player=inviter, name=post_data['guest'])
        self.assertTrue(guest.inviting_date != None)

        self.assertEquals(len(mail.outbox), 1)


    def test_add_guest_after(self):
        """
        Add guest view should return 400 if match has already been played.
        """
        # setup initial data
        match = Match.objects.create(date=datetime.now() - timedelta(seconds=1), place='Somewhere')
        inviter = Player.objects.create(name='Inviter', email='inviter@email.com')
        other_player = Player.objects.create(name='Other Player', email='other@player.com')
        match.matchplayer_set.create(player=inviter)
        match.matchplayer_set.create(player=other_player)
        guest_count = Guest.objects.count()

        # make the request
        c = Client()
        post_data = {
            'inviting_player': inviter.id,
            'guest': 'Invitee',
        }
        response = c.post('/matches/%d/addguest/' % match.id, post_data, follow=True)

        # make assertions
        self.assertEquals(response.status_code, 400)

        guest = Guest.objects.filter(match=match, inviting_player=inviter, name=post_data['guest'])
        self.assertFalse(guest.exists())
        self.assertEquals(guest_count, Guest.objects.count())

        self.assertEquals(len(mail.outbox), 0)


    def test_remove_guest(self):
        """
        The guest should be removed from the match if conditions are met.
        """

        # bad method
        c = Client()
        response = c.post('/removeguest/123/')
        self.assertEquals(response.status_code, 405)

        # bad guest_id
        response = c.get('/removeguest/1234/')
        self.assertEquals(response.status_code, 404)

        # match has already been played
        match1 = Match.objects.create(date=datetime.now() - timedelta(days=1), place='Field')
        player1 = Player.objects.create(name='Maria Juana', email='mary@jane.org')
        match1.matchplayer_set.create(player=player1)
        guest1 = Guest.objects.create(match=match1, inviting_player=player1, name='Bud')
        response = c.get('/removeguest/%i/' % guest1.id)
        self.assertEquals(response.status_code, 400)

        # everything ok
        match2 = Match.objects.create(date=datetime.now() + timedelta(days=1), place='Colombia')
        player2 = Player.objects.create(name='Pablo Escobar', email='escobar@cocacola.org')
        match2.matchplayer_set.create(player=player1)
        match2.matchplayer_set.create(player=player2)
        guest2 = Guest.objects.create(match=match2, inviting_player=player2, name='El Pibe')
        response = c.get('/removeguest/%i/' % guest2.id, follow=True)
        self.assertEquals(response.status_code, 200)

        # guest should be removed
        self.assertFalse(Guest.objects.filter(id=guest2.id).exists())

        # emails should be sent
        self.assertEquals(len(mail.outbox), 1)

        # user should be redirected to match
        self.assertEquals(response.context['match'], match2)
        self.assertEquals(response.templates[0].name, 'core/match.html')


    def test_send_mail_view(self):
        """
        Test send mail view.
        """
        c = Client()
        match_count = Match.objects.count()
        response = c.post('/sendmail/')

        Player.objects.create(name='Diego Armando', email='diego@rmando.net')
        Player.objects.create(name='O Rei', email='pele@brasil.net')

        self.assertTrue(response.status_code == 201 or response.status_code == 204)

        if response.status_code == 201:
            self.assertEquals(match_count + 1, Match.objects.count())
        elif response.status_code == 204:
            self.assertEquals(match_count, Match.objects.count())


    def test_current_player(self):
        """
        Test that current player is properly set and retrieved from session.
        """
        # base case
        c = Client()
        response = c.get('/')
        self.assertFalse('player_id' in c.session)

        # store player in session
        player = Player.objects.create(name='Jimmy Page', email='jpage@zeppelin.com')
        response = c.get('/?player_id=%i' % player.id)
        self.assertTrue('player_id' in c.session)
        self.assertEquals(c.session['player_id'], player.id)

        # session is persisted
        response = c.get('/')
        self.assertTrue('player_id' in c.session)
        self.assertEquals(c.session['player_id'], player.id)

        # remove player from session if bad id
        response = c.get('/?player_id=12345')
        self.assertFalse('player_id' in c.session)


# Tasks tests

class TasksTests(TestCase):
    """
    TestCase subclass for the tasks module.
    """

    def assert_datetime_equals(self, date1, date2, new_day):
        """
        Helper method for comparing two datetimes, where date2 is equal to date1
        except for the day which should be equal to new_day.
        """
        self.assertEquals(date2.year, date1.year)
        self.assertEquals(date2.month, date1.month)
        self.assertEquals(date2.day, new_day)
        self.assertEquals(date2.hour, date1.hour)
        self.assertEquals(date2.minute, date1.minute)
        self.assertEquals(date2.second, date1.second)
        self.assertEquals(date2.microsecond, date1.microsecond)


    def test_next_weekday(self):
        """
        next_weekday should return the date corresponding to the next given
        weekday, starting from the given base date.
        """
        wed = datetime(2015, 2, 11, 18, 39, 59, 1234)

        next_wed = tasks.next_weekday(wed, 2)
        self.assert_datetime_equals(wed, next_wed, 11)

        next_fri = tasks.next_weekday(wed, 4)
        self.assert_datetime_equals(wed, next_fri, 13)

        next_mon = tasks.next_weekday(wed, 0)
        self.assert_datetime_equals(wed, next_mon, 16)


    def test_set_hour(self):
        """
        set_hour should set the given hour to the given date and reset the rest
        of the time components to zero.
        """
        date = datetime(2015, 2, 11, 18, 39, 59, 1234)
        date = tasks.set_hour(date, 7)
        expected_date = datetime(2015, 2, 11, 7, 0, 0, 0)
        self.assertEquals(date, expected_date)


    def test_find_or_create_match(self):
        """
        Should find or create a match for the given date and send proper emails.
        """
        date = datetime(2015, 3, 23, 7, 0, 0, 0)

        # create match
        Player.objects.create(name='Player One', email='p1@email.com')
        Player.objects.create(name='Player Two', email='p2@email.com')
        Player.objects.create(name='Player Three', email='p3@email.com')
        Player.objects.create(name='Player Four', email='p4@email.com')

        match_count = Match.objects.count()
        match = tasks.find_or_create_match(date)

        self.assertTrue(match != None)
        self.assertEquals(match.date, date)
        self.assertEquals(Match.objects.count(), match_count + 1)
        self.assertEquals(len(mail.outbox), Player.objects.count())
        mail.outbox = []

        # find match
        p1 = Player.objects.create(name='Match Player One', email='mp1@email.com')
        match.matchplayer_set.create(player=p1)
        p2 = Player.objects.create(name='Match Player Two', email='mp2@email.com')
        match.matchplayer_set.create(player=p2)

        match_count = Match.objects.count()
        match = tasks.find_or_create_match(date)

        self.assertTrue(match != None)
        self.assertEquals(match.date, date)
        self.assertEquals(Match.objects.count(), match_count)
        self.assertEquals(len(mail.outbox), Player.objects.count())


    def test_create_match_or_send_status(self):
        """
        Test the create_match_or_send_status function.
        Should find or create a match for next Wednesday or next Friday and send
        proper emails on weekdays, shoud rest on weekends.
        """
        # create players
        Player.objects.create(name='Player One', email='p1@email.com')
        Player.objects.create(name='Player Two', email='p2@email.com')
        Player.objects.create(name='Player Three', email='p3@email.com')
        Player.objects.create(name='Player Four', email='p4@email.com')

        # Monday 7:15 AM
        match_count = Match.objects.count()

        date = datetime(2015, 3, 23, 7, 15, 0, 0)
        match = tasks.create_match_or_send_status(date)

        self.assertTrue(match != None)
        self.assertEquals(match.date, datetime(2015, 3, 25, 19, 0, 0, 0))
        self.assertEquals(Match.objects.count(), match_count + 1)
        self.assertEquals(len(mail.outbox), Player.objects.count())
        mail.outbox = []

        # add players
        p1 = Player.objects.create(name='Match Player One', email='mp1@email.com')
        match.matchplayer_set.create(player=p1)
        p2 = Player.objects.create(name='Match Player Two', email='mp2@email.com')
        match.matchplayer_set.create(player=p2)

        # Wednesday 3:00 PM
        match_count = Match.objects.count()

        date = datetime(2015, 3, 25, 15, 0, 0, 0)
        match = tasks.create_match_or_send_status(date)

        self.assertTrue(match != None)
        self.assertEquals(match.date, datetime(2015, 3, 25, 19, 0, 0, 0))
        self.assertEquals(Match.objects.count(), match_count)
        self.assertEquals(len(mail.outbox), Player.objects.count())
        mail.outbox = []

        # Thursday  7:00 AM
        match_count = Match.objects.count()

        date = datetime(2015, 3, 26, 7, 0, 0, 0)
        match = tasks.create_match_or_send_status(date)

        self.assertTrue(match != None)
        self.assertEquals(match.date, datetime(2015, 3, 27, 20, 0, 0, 0))
        self.assertEquals(Match.objects.count(), match_count + 1)
        self.assertEquals(len(mail.outbox), Player.objects.count())
        mail.outbox = []

        # add players
        fp1 = Player.objects.create(name='Friday One', email='fri1@email.com')
        match.matchplayer_set.create(player=fp1)
        fp2 = Player.objects.create(name='Friday Two', email='fri2@email.com')
        match.matchplayer_set.create(player=fp2)

        # Friday  7:00 AM
        match_count = Match.objects.count()

        date = datetime(2015, 3, 27, 7, 0, 0, 0)
        match = tasks.create_match_or_send_status(date)

        self.assertTrue(match != None)
        self.assertEquals(match.date, datetime(2015, 3, 27, 20, 0, 0, 0))
        self.assertEquals(Match.objects.count(), match_count)
        self.assertEquals(len(mail.outbox), Player.objects.count())
        mail.outbox = []

        # Sunday
        match_count = Match.objects.count()

        date = datetime(2015, 3, 29, 2, 0, 0, 0)
        match = tasks.create_match_or_send_status(date)

        self.assertTrue(match == None)
        self.assertEquals(Match.objects.count(), match_count)
        self.assertEquals(len(mail.outbox), 0)


# Mailer tests

class MailerTests(TestCase):
    """
    Test case subclass for the mailer module.
    """

    def test_email_address(self):
        """
        Test email address generation.
        """
        player = Player.objects.create(name='Ringo Starr', email='ringo@beatles.com')
        address = mailer.email_address(player)
        self.assertEquals(address, '%s <%s>' % (player.name, player.email))


    def test_invite_message(self):
        """
        Test the invite message.
        """
        player = Player.objects.create(name='George Harrison', email='george@beatles.com')
        match = Match.objects.create(date=datetime.now(), place='Somewhere')
        msg = mailer.invite_message(match, player)
        self.assertEquals(msg.subject, 'Fobal')
        self.assertEquals(msg.from_email, 'Fobal <noreply@fobal.com>')
        self.assertEquals(msg.to, [mailer.email_address(player)])
        self.assertTrue('Hola %s' % player.name in msg.body)
        self.assertTrue(match.place in msg.body)
        self.assertTrue(match_url(match, player) in msg.body)
        self.assertTrue(join_match_url(match, player) in msg.body)
        self.assertTrue(leave_match_url(match, player) in msg.body)


    def test_send_invite_mails(self):
        """
        Test sending invite messages.
        """
        match = Match.objects.create(date=datetime.now(), place='Here')
        player1 = Player.objects.create(name='Juan Pedro', email='jp@fasola.com')
        player2 = Player.objects.create(name='Juan Ramon', email='jr@carrasco.com')

        players = [player1, player2]

        mailer.send_invite_mails(match, players)

        self.assertEquals(len(mail.outbox), len(players))


    def test_leave_match_message(self):
        """
        Test the leave match message.
        """
        canario = Player.objects.create(name='Washington Luna', email='canario@villaespañola.org')
        jaime = Player.objects.create(name='Jaime Roos', email='jaime@defensor.com')
        match = Match.objects.create(date=datetime.now(), place='Centenario')
        match.matchplayer_set.create(player=canario)
        match.save()
        msg = mailer.leave_match_message(match, canario, jaime)
        self.assertEquals(msg.subject, 'Fobal')
        self.assertEquals(msg.from_email, 'Fobal <noreply@fobal.com>')
        self.assertEquals(msg.to, [mailer.email_address(canario)])
        self.assertTrue('Hola %s' % canario.name in msg.body)
        self.assertTrue(match.place in msg.body)
        self.assertTrue(match_url(match, canario) in msg.body)
        self.assertTrue(jaime.name in msg.body)


    def test_send_leave_mails(self):
        """
        Test sending leave messages.
        """
        canario = Player.objects.create(name='Washington Luna', email='canario@villaespañola.org')
        jaime = Player.objects.create(name='Jaime Roos', email='jaime@defensor.com')
        match = Match.objects.create(date=datetime.now(), place='Centenario')
        match.matchplayer_set.create(player=jaime)
        match.save()

        msg = mailer.send_leave_mails(match, canario)
        self.assertEquals(len(mail.outbox), 1, 'Should send an email to Jaime')

        msg = mail.outbox[0]
        self.assertEquals(msg.subject, 'Fobal')
        self.assertEquals(msg.from_email, 'Fobal <noreply@fobal.com>')
        self.assertEquals(msg.to, [mailer.email_address(jaime)])
        self.assertTrue('Hola %s' % jaime.name in msg.body)
        self.assertTrue(match.place in msg.body)
        self.assertTrue(match_url(match, jaime) in msg.body)
        self.assertTrue(canario.name in msg.body)


    def test_join_match_message(self):
        """
        Test the join match message.
        """
        mateo = Player.objects.create(name='Eduardo Mateo', email='eduardo@tartamudo.org')
        rada = Player.objects.create(name='Ruben Rada', email='rada@candombe.com')
        match = Match.objects.create(date=datetime.now(), place='Franzini')
        match.matchplayer_set.create(player=mateo)
        match.save()

        msg = mailer.join_match_message(match, mateo, rada)
        self.assertEquals(msg.subject, 'Fobal')
        self.assertEquals(msg.from_email, 'Fobal <noreply@fobal.com>')
        self.assertEquals(msg.to, [mailer.email_address(mateo)])
        self.assertTrue('Hola %s' % mateo.name in msg.body)
        self.assertTrue(match.place in msg.body)
        self.assertTrue(match_url(match, mateo) in msg.body)
        self.assertTrue(rada.name in msg.body)


    def test_send_join_mails(self):
        """
        Test sending join messages.
        """
        mateo = Player.objects.create(name='Eduardo Mateo', email='eduardo@tartamudo.org')
        rada = Player.objects.create(name='Ruben Rada', email='rada@candombe.com')
        match = Match.objects.create(date=datetime.now(), place='Franzini')
        match.matchplayer_set.create(player=rada)
        match.matchplayer_set.create(player=mateo)
        match.save()

        msg = mailer.send_join_mails(match, mateo)
        self.assertEquals(len(mail.outbox), 1, 'Should send an email to Rada')

        msg = mail.outbox[0]
        self.assertEquals(msg.subject, 'Fobal')
        self.assertEquals(msg.from_email, 'Fobal <noreply@fobal.com>')
        self.assertEquals(msg.to, [mailer.email_address(rada)])
        self.assertTrue('Hola %s' % rada.name in msg.body)
        self.assertTrue(match.place in msg.body)
        self.assertTrue(match_url(match, rada) in msg.body)
        self.assertTrue(mateo.name in msg.body)


    def test_invite_guest_message(self):
        """
        Test the invite guest message.
        """
        match = Match.objects.create(date=datetime.now(), place='Guest Field')
        player = Player.objects.create(name='Guest Mail Receiver', email='receiver@guest.com')
        inviting_player = Player.objects.create(name='Guest Inviter', email='inviter@guest.com')
        guest = Guest.objects.create(name='Guest', inviting_player=inviting_player, match=match)

        msg = mailer.invite_guest_message(match, player, inviting_player, guest)
        self.assertEquals(msg.subject, 'Fobal')
        self.assertEquals(msg.from_email, 'Fobal <noreply@fobal.com>')
        self.assertEquals(msg.to, [mailer.email_address(player)])
        self.assertTrue('Hola %s' % player.name in msg.body)
        self.assertTrue(match.place in msg.body)
        self.assertTrue(match_url(match, player) in msg.body)
        self.assertTrue(inviting_player.name in msg.body)
        self.assertTrue(guest.name in msg.body)


    def test_send_invite_guest_mails(self):
        """
        Test sending guest invite messages.
        """
        match = Match.objects.create(date=datetime.now(), place='Guest Field')
        player = Player.objects.create(name='Guest Mail Receiver', email='receiver@guest.com')
        inviting_player = Player.objects.create(name='Guest Inviter', email='inviter@guest.com')
        match.matchplayer_set.create(player=player)
        match.matchplayer_set.create(player=inviting_player)
        guest = Guest.objects.create(name='Guest', inviting_player=inviting_player, match=match)

        mailer.send_invite_guest_mails(match, inviting_player, guest)
        self.assertEquals(len(mail.outbox), 1)

        msg = mail.outbox[0]
        self.assertEquals(msg.subject, 'Fobal')
        self.assertEquals(msg.from_email, 'Fobal <noreply@fobal.com>')
        self.assertEquals(msg.to, [mailer.email_address(player)])


    def test_remove_guest_message(self):
        """
        Test the remove guest message.
        """
        match = Match.objects.create(date=datetime.now(), place='Guest Field')
        player = Player.objects.create(name='Guest Mail Receiver', email='receiver@guest.com')
        inviting_player = Player.objects.create(name='Guest Inviter', email='inviter@guest.com')
        guest = Guest.objects.create(name='Guest', inviting_player=inviting_player, match=match)

        msg = mailer.remove_guest_message(guest, player)
        self.assertEquals(msg.subject, 'Fobal')
        self.assertEquals(msg.from_email, 'Fobal <noreply@fobal.com>')
        self.assertEquals(msg.to, [mailer.email_address(player)])
        self.assertTrue('Hola %s' % player.name in msg.body)
        self.assertTrue(match.place in msg.body)
        self.assertTrue(match_url(match, player) in msg.body)
        self.assertTrue(inviting_player.name in msg.body)
        self.assertTrue(guest.name in msg.body)


    def test_send_remove_guest_mails(self):
        """
        Test sending guest remove messages.
        """
        match = Match.objects.create(date=datetime.now(), place='Guest Field')
        player = Player.objects.create(name='Guest Mail Receiver', email='receiver@guest.com')
        inviting_player = Player.objects.create(name='Guest Inviter', email='inviter@guest.com')
        match.matchplayer_set.create(player=player)
        match.matchplayer_set.create(player=inviting_player)
        guest = Guest.objects.create(name='Guest', inviting_player=inviting_player, match=match)

        mailer.send_remove_guest_mails(guest)
        self.assertEquals(len(mail.outbox), 1)

        msg = mail.outbox[0]
        self.assertEquals(msg.subject, 'Fobal')
        self.assertEquals(msg.from_email, 'Fobal <noreply@fobal.com>')
        self.assertEquals(msg.to, [mailer.email_address(player)])


    def test_status_message(self):
        """
        Status message should contain the number of players in the match and
        the match URL.
        """
        match = Match.objects.create(date=datetime.now(), place='Status')
        p1 = Player.objects.create(name='Status One', email='status1@email.com')
        match.matchplayer_set.create(player=p1)
        p2 = Player.objects.create(name='Status Two', email='status2@email.com')
        match.matchplayer_set.create(player=p2)
        g = match.guests.create(name='Guest One', inviting_player=p1)

        msg = mailer.status_message(match, p1)
        self.assertEquals(msg.subject, 'Fobal')
        self.assertEquals(msg.from_email, 'Fobal <noreply@fobal.com>')
        self.assertEquals(msg.to, [mailer.email_address(p1)])
        self.assertTrue('Hola %s' % p1.name in msg.body)
        self.assertTrue(match.place in msg.body)
        self.assertTrue(match_url(match, p1) in msg.body)
        self.assertTrue('%i jugadores' % 3 in msg.body)


    def test_send_status_mails(self):
        """
        Test sending status messages.
        """
        match = Match.objects.create(date=datetime.now(), place='Status Field')
        p1 = Player.objects.create(name='Status One', email='status1@email.com')
        p2 = Player.objects.create(name='Status Two', email='status2@email.com')

        mailer.send_status_mails(match, Player.objects.all())
        self.assertEquals(len(mail.outbox), 2)


# URL helper tests

class UrlHelperTests(TestCase):
    """
    TestCase subclass for the urlhelper module.
    """

    def test_absolute_url(self):
        """
        Test creating an absolute URL from a relative URL.
        """
        base = settings.BASE_URL
        relative = 'myrelativeurl'
        absolute = absolute_url(relative)
        self.assertEquals(absolute, urljoin(base, relative))


    def test_join_match_url(self):
        """
        Test the join match URL.
        """
        match = Match(id=1)
        player = Player(id=2)
        url = join_match_url(match, player)
        self.assertEquals(url, '/matches/1/join/2/')


    def test_leave_match_url(self):
        """
        Test the leave match URL.
        """
        match = Match(id=3)
        player = Player(id=4)
        url = leave_match_url(match, player)
        self.assertEquals(url, '/matches/3/leave/4/')


    def test_match_url(self):
        """
        Test the match URL contains the player id as a query parameter if set.
        """
        match = Match(id=5)
        player = Player(id=7)
        url = match_url(match, player)
        self.assertEquals(url, '/matches/5/?player_id=7')

        url = match_url(match, None)
        self.assertEquals(url, '/matches/5/')
