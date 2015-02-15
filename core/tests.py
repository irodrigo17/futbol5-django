from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import datetime
from urlparse import urljoin

from core.models import Player, Match, MatchPlayer
from core import tasks, mailer

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

    def test_top_player(self):
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
        self.assertEquals(response.context['top_player'], Player.top_player())
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


# Tasks tests

class TasksTests(TestCase):

    def assert_datetime_equals(self, date1, date2, new_day):
        self.assertEquals(date2.year, date1.year)
        self.assertEquals(date2.month, date1.month)
        self.assertEquals(date2.day, new_day)
        self.assertEquals(date2.hour, date1.hour)
        self.assertEquals(date2.minute, date1.minute)
        self.assertEquals(date2.second, date1.second)
        self.assertEquals(date2.microsecond, date1.microsecond)


    def test_next_weekday(self):
        wed = datetime(2015, 2, 11, 18, 39, 59, 1234)

        next_fri = tasks.next_weekday(wed, 4)
        self.assert_datetime_equals(wed, next_fri, 13)

        next_wed = tasks.next_weekday(wed, 2)
        self.assert_datetime_equals(wed, next_wed, 18)

        next_mon = tasks.next_weekday(wed, 0)
        self.assert_datetime_equals(wed, next_mon, 16)


    def test_default_weekdays_and_times(self):
        weekdays = tasks.default_weekdays_and_times()
        self.assertEquals(weekdays[0]['weekday'], 2)
        self.assertEquals(weekdays[0]['hour'], 19)
        self.assertEquals(weekdays[1]['weekday'], 4)
        self.assertEquals(weekdays[1]['hour'], 20)


    def test_week_dates(self):
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
        self.assertEquals(tasks.default_place(), 'River')


    def test_create_matches(self):
        expected_dates = tasks.week_dates(datetime.now(), tasks.default_weekdays_and_times())
        expected_place = tasks.default_place()
        matches = tasks.create_matches()
        self.assertEquals(len(matches), len(expected_dates))
        for i in range(len(matches)):
            self.assertEquals(matches[i].date, expected_dates[i])
            self.assertEquals(matches[i].place, expected_place)



# Mailer tests

class MailerTests(TestCase):

    def test_absolute_url(self):
        base = settings.BASE_URL
        relative = 'myrelativeurl'
        absolute = mailer.absolute_url(relative)
        self.assertEquals(absolute, urljoin(base, relative))

    def test_join_match_url(self):
        match = Match(id=1)
        player = Player(id=2)
        url = mailer.join_match_url(match, player)
        self.assertTrue('/matches/1/join/2/' in url)
        self.assertTrue('://' in url, 'URL should be absolute')


    def test_leave_match_url(self):
        match = Match(id=3)
        player = Player(id=4)
        url = mailer.leave_match_url(match, player)
        self.assertTrue('/matches/3/leave/4/' in url)
        self.assertTrue('://' in url, 'URL should be absolute')


    def test_email_template_context(self):
        match = Match(id=3)
        player = Player(id=4)
        context = mailer.email_template_context(match, player)
        self.assertEquals(context['match'], match)
        self.assertEquals(context['player'], player)
        self.assertEquals(context['join_match_url'], mailer.join_match_url(match, player))
        self.assertEquals(context['leave_match_url'], mailer.leave_match_url(match, player))


    def test_text_content(self):
        match = Match.objects.create(date=datetime.now(), place='Somewhere')
        player = Player.objects.create(name='John Lennon', email='john@beatles.com')
        msg = mailer.text_content(match, player)
        expected_greeting = 'Hola %s' % player.name
        expected_join_match_path = '/matches/%d/join/%d/' % (match.id, player.id)
        expected_leave_match_path = '/matches/%d/leave/%d/' % (match.id, player.id)
        self.assertTrue(expected_greeting in msg)
        self.assertTrue(expected_join_match_path in msg)
        self.assertTrue(expected_leave_match_path in msg)

    def test_html_content(self):
        match = Match.objects.create(date=datetime.now(), place='Somewhere')
        player = Player.objects.create(name='Paul McCartney', email='paul@beatles.com')
        msg = mailer.html_content(match, player)
        expected_greeting = 'Hola %s' % player.name
        expected_join_match_path = '/matches/%d/join/%d/' % (match.id, player.id)
        expected_leave_match_path = '/matches/%d/leave/%d/' % (match.id, player.id)
        self.assertTrue(expected_greeting in msg)
        self.assertTrue(expected_join_match_path in msg)
        self.assertTrue(expected_leave_match_path in msg)

    def test_email_address(self):
        player = Player.objects.create(name='Ringo Starr', email='ringo@beatles.com')
        address = mailer.email_address(player)
        self.assertEquals(address, '%s <%s>' % (player.name, player.email))

    def test_email_message(self):
        player = Player.objects.create(name='George Harrison', email='george@beatles.com')
        match = Match.objects.create(date=datetime.now(), place='Somewhere')
        email_message = mailer.email_message(match, player)
        self.assertEquals(email_message.subject, 'Fobal')
        self.assertEquals(email_message.body, mailer.text_content(match, player))
        self.assertEquals(email_message.from_email, 'Fobal <noreply@fobal.com>')
        self.assertEquals(email_message.to, [mailer.email_address(player)])
