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
from core import tasks, mailer, views
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
        and match has not been played yet
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


    def test_match_view_with_valid_player(self):
        """
        Match view with a valid player should render properly.
        """
        c = Client()
        match = Match.objects.create(date=datetime.now(), place="La Cancha")
        player = Player.objects.create(name='Test Match View', email="test@matchview.com")
        response = c.get('/matches/%d/' % match.id, {'player_id': player.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['match'], match)
        self.assertEquals(response.context['player'], player)
        self.assertEquals(response.templates[0].name, 'core/match.html')
        self.assertTrue("<form action=\"addguest/\" method=\"post\">" in str(response.content))


    def test_match_view_with_invalid_player(self):
        """
        Match view with an invalid player should render as if there were no player.
        """
        c = Client()
        match = Match.objects.create(date=datetime.now(), place="La Cancha")
        response = c.get('/matches/%d/' % match.id, {'player_id': 12345})
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


    def test_send_mail_view_debug(self):
        """
        Test debug send mail view.
        """
        match = Match.objects.create(date=datetime.now(), place='There')
        player = Player.objects.create(name='My Player', email='my@player.com')

        c = Client()
        response = c.get('/sendmail/', {'player': player.id, 'match': match.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 1, "Should send one email")
        self.assertTrue('/matches/%i/join/%i/' % (match.id, player.id) in mail.outbox[0].body)
        self.assertTrue('/matches/%i/leave/%i/' % (match.id, player.id) in mail.outbox[0].body)


    def test_send_mail_view(self):
        """
        Test send mail view.
        """
        prev_matches = Match.objects.count()

        c = Client()
        response = c.get('/sendmail/')

        matches = Match.objects.count()
        self.assertTrue(matches > prev_matches)

        expected_emails = (matches - prev_matches) * Player.objects.count()
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(mail.outbox), expected_emails, "Should send one email per match per player")


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
        Helper method for comparing two datetimes.
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
        Test next weekday.
        """
        wed = datetime(2015, 2, 11, 18, 39, 59, 1234)

        next_fri = tasks.next_weekday(wed, 4)
        self.assert_datetime_equals(wed, next_fri, 13)

        next_wed = tasks.next_weekday(wed, 2)
        self.assert_datetime_equals(wed, next_wed, 18)

        next_mon = tasks.next_weekday(wed, 0)
        self.assert_datetime_equals(wed, next_mon, 16)


    def test_default_weekdays_and_times(self):
        """
        Test default weekdays and times.
        """
        weekdays = tasks.default_weekdays_and_times()
        self.assertEquals(weekdays[0]['weekday'], 2)
        self.assertEquals(weekdays[0]['hour'], 19)
        self.assertEquals(weekdays[1]['weekday'], 4)
        self.assertEquals(weekdays[1]['hour'], 20)


    def test_week_dates(self):
        """
        Test week dates.
        """
        now = datetime.now()
        weekdays_and_times = tasks.default_weekdays_and_times()

        week_dates = tasks.week_dates(now, weekdays_and_times)

        self.assertEquals(len(week_dates), len(weekdays_and_times))

        for i in range(len(week_dates)):
            wd = weekdays_and_times[i]
            expected_date = tasks.next_weekday(now, wd['weekday'])
            expected_hour = wd['hour']
            date = week_dates[i]

            self.assertEquals(date.year, expected_date.year)
            self.assertEquals(date.month, expected_date.month)
            self.assertEquals(date.day, expected_date.day)
            self.assertEquals(date.hour, expected_hour)
            self.assertEquals(date.minute, 0)
            self.assertEquals(date.second, 0)
            self.assertEquals(date.microsecond, 0)


    def test_default_place(self):
        """
        Test default place.
        """
        self.assertEquals(tasks.default_place(), 'River')


    def test_create_matches(self):
        """
        Test the create_matches function.
        """
        expected_dates = tasks.week_dates(datetime.now(), tasks.default_weekdays_and_times())
        expected_place = tasks.default_place()
        matches = tasks.create_matches()
        self.assertEquals(len(matches), len(expected_dates))
        for i in range(len(matches)):
            self.assertEquals(matches[i].date, expected_dates[i])
            self.assertEquals(matches[i].place, expected_place)



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
        match1 = Match.objects.create(date=datetime.now(), place='Here')
        match2 = Match.objects.create(date=datetime.now(), place='There')
        player1 = Player.objects.create(name='Juan Pedro', email='jp@fasola.com')
        player2 = Player.objects.create(name='Juan Ramon', email='jr@carrasco.com')

        matches = [match1, match2]
        players = [player1, player2]

        mailer.send_invite_mails(matches, players)

        self.assertEquals(len(mail.outbox), len(matches) * len(players))


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
        Test sengind guest invite messages.
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
        Test the match URL contains the player id as a query parameter.
        """
        match = Match(id=5)
        player = Player(id=7)
        url = match_url(match, player)
        self.assertEquals(url, '/matches/5/?player_id=7')
