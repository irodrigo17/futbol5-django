# Futbol 5

[![TravisCI](https://travis-ci.org/irodrigo17/futbol5-django.svg?branch=master)](https://travis-ci.org/irodrigo17/futbol5-django)
[![Coverage Status](https://coveralls.io/repos/irodrigo17/futbol5-django/badge.svg?branch=master)](https://coveralls.io/r/irodrigo17/futbol5-django?branch=master)

Very basic [Django](https://www.djangoproject.com) app for managing weekly soccer matches.

Basically, it just creates matches every week and emails a join link to players.

Based on the [Futbol 5 Rails app](https://github.com/irodrigo17/fulbol5).


## Tech stuff

Running on Python 3.4.2 and Django 1.7.4 and deployed to [Heroku](https://fobal.herokuapp.com).

Using [PostgreSQL](http://www.postgresql.org) as the database backend.

Sending mails with the [default Django SMTP email backend](https://docs.djangoproject.com/en/1.7/topics/email/). Using [Mandrill](http://mandrill.com) in production and a test Gmail account for development.

Using the [Temporize Add-On](https://www.temporize.net/) to `GET /sendmail` every monday in order to create week matches and send invite emails. Not as pretty as [celery](http://www.celeryproject.org) but running a second dyno is not free.

Dependencies can be installed using `pip install -r requirements.txt`, using [virtualenv](https://virtualenv.pypa.io/) is recommended.

Database is migrated using the default [Django Migrations](https://docs.djangoproject.com/en/1.7/topics/migrations/) by running `python manage.py migrate`.

Using [foreman](https://github.com/ddollar/foreman) and a `.env` file can help to run the processes in the `Procfile` with all the needed environment variables set (see environment variables below).

Tests can be run with `foreman run test`.

Local server can be run with `foreman start web`.

Using [TravisCI](https://travis-ci.org/irodrigo17/futbol5-django) for continuous integration and [Coveralls](https://coveralls.io/r/irodrigo17/futbol5-django) for test coverage.



#### Environment variables

There are some environment variables that need to be set for the app to work properly, namely:

- `DATABASE_URL` - The URL of the the PostgreSQL database, example: `postgres://localhost/fobal`.
- `DJANGO_DEBUG` - Set to enable debug mode, remove in production.
- `DJANGO_TEMPLATE_DEBUG` - Set to enable template debug mode, remove in production.
- `DJANGO_SECRET_KEY` - The secret key used for [cryptographic signing](https://docs.djangoproject.com/en/1.7/topics/signing/), example: `#$w7h4e_!_un6et##xgwtieb_70o$1wwx@p05cgyczt7mkui(p`.
- `DJANGO_EMAIL_HOST` - The email host for sending SMTP emails, example: `smtp.gmail.com`.
- `DJANGO_EMAIL_HOST_USER` - The user for sending SMTP emails, example: `futbol5.dev`.
- `DJANGO_EMAIL_HOST_PASSWORD` - The password for sending SMTP emails, example: `Fu7b0l5_D3V`.


## TODOs

- [x] Create basic match view
- [x] Add tests
- [x] Deploy to [Heroku](https://devcenter.heroku.com/articles/getting-started-with-python)
- [x] Fix timezone warning
- [x] Fix static files serving on Heroku
- [x] Create CRON Job to create matches and send emails
- [x] Format and localize match date in emails and views
- [x] Integrate [TravisCI](https://travis-ci.org/)
- [x] Remove all celery stuff if the temporize add-on works out
- [x] Remove debug code from send_mail view
- [x] Seed DB with default players
- [x] Check test coverage
- [x] Switch to python 3
- [x] **Go Live!**
- [x] Notify players when a player leaves a match
- [x] Notify players when a player joins a match
- [x] Add weekday to match date
- [ ] Setup logging and log important information (match creation, email sending, players joining / leaving)
- [ ] Invite external friends to a match (notify players)
- [ ] Cancel matches (notify players and save stats)
- [ ] Delete player / unsuscribe (save stats)
- [ ] Send email notification the day of the match, include player list and optional friend invitations if len(match.players) < 10
- [ ] Improve UI
- [ ] Store player first and last names separately, and use only first name in emails
- [ ] Edit match time and place (notify players)
- [ ] Save stats of players leaving matches
- [ ] Add static code analysis
- [ ] Players can perform CRUD operations on matches on the site, maybe voting or some kind of democratic decision making protocol can help
