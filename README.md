# Futbol 5

[![TravisCI](https://travis-ci.org/irodrigo17/futbol5-django.svg?branch=master)](https://travis-ci.org/irodrigo17/futbol5-django)

Very basic [Django](https://www.djangoproject.com) app for managing weekly soccer matches.

Basically, it just creates matches every week and emails a join link to players.

Based on the [Futbol 5 Rails app](https://github.com/irodrigo17/fulbol5).


## Tech stuff

Running on Python 2.7 and Django 1.7 and deployed to [Heroku](https://fobal.herokuapp.com).

Using [PostgreSQL](http://www.postgresql.org) as the database backend.

Sending mails with the [default Django SMTP email backend](https://docs.djangoproject.com/en/1.7/topics/email/).

Using the [Temporize Add-On](https://www.temporize.net/) to `GET /sedmail` every monday in order to create week matches and send invite emails, not as pretty as celery but hey, running a second dyno isn't free.

Dependencies can be installed using `pip install`.

Tests can be run with `python manage.py test`.


#### Environment variables

There are some environment variables that need to be set for the app to work properly, namely:

- `DATABASE_URL` - The URL of the the PostgreSQL database, example: `postgres://localhost/fobal`.
- `DJANGO_DEBUG` - A boolean flag (`True` or `False`) to set Django debug mode. Should be `True` for development and `False` in production, always.
- `DJANGO_TEMPLATE_DEBUG` - A boolean flag (`True` or `False`) to set Django template debug mode. Should be `True` for development and `False` in production, always.
- `DJANGO_SECRET_KEY` - The secret key used for [cryptographic signing](https://docs.djangoproject.com/en/1.7/topics/signing/), example: `#$w7h4e_!_un6et##xgwtieb_70o$1wwx@p05cgyczt7mkui(p`.
- `DJANGO_EMAIL_HOST` - The email host for sending SMTP emails, example: `smtp.gmail.com`.
- `DJANGO_EMAIL_HOST_USER` - The user for sending SMTP emails, example: `futbol5.dev`.
- `DJANGO_EMAIL_HOST_PASSWORD` - The password for sending SMTP emails, example: `Fu7b0l5_D3V`.

[foreman](https://github.com/ddollar/foreman) and a `.env` file can help to run the processes in the `Procfile` with all the environment variables set.


## TODOs

- [x] Create basic match view
- [x] Add tests
- [x] Deploy to [Heroku](https://devcenter.heroku.com/articles/getting-started-with-python)
- [x] Fix timezone warning
- [x] Fix static files serving on Heroku
- [x] Create CRON Job to create matches and send emails [django-crontab](https://github.com/kraiz/django-crontab)
- [x] Format and localize match date in emails and views
- [x] Integrate [TravisCI](https://travis-ci.org/)
- [x] Remove all celery stuff if the temporize add-on works out
- [ ] Remove debug code from send_mail view
- [ ] Seed DB with default players
- [ ] ------------- Go Live! ------------
- [ ] Store player first and last names separately, and use only first name in emails
- [ ] Improve UI
- [ ] Delete player / unsuscribe
- [ ] Notify players when a player leaves a match
- [ ] Cancel matches (notify players)
- [ ] Invite external friends to a match (notify players)
- [ ] Edit match time and place (notify players)
- [ ] Send email notification a day before a match with players list, add optional friend invitations if len(match.players) < 10
- [ ] Switch to python 3
- [ ] Check test coverage
- [ ] Add static code analysis
