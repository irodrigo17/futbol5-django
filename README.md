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

Using some very basic [Bootstrap](http://getbootstrap.com) styles.

Using [Django Rest Framework](http://www.django-rest-framework.org) to expose a RESTful API.


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
- [x] Setup logging and log important information (match creation, email sending, players joining / leaving)
- [x] Invite external friends to a match (notify players)
- [x] Mobile-friendly
- [x] Improve UI
- [x] Match invitation emails include match URL
- [x] Keep player info (cookies)
- [x] Expose a RESTful API using [Django Rest Framework](http://www.django-rest-framework.org)
- [ ] Fix next match (probably a timezone issue)
- [ ] Send daily email notifications with the status of the next match
- [ ] Use [AngularJS](https://angularjs.org) for the frontend
- [ ] Players can delete invited friends from the web (notify players)
- [ ] Players can join or leave a match from the web
- [ ] Send mails when models are saved (so Django admin and API work)
- [ ] Add flash messages when joining/leaving/inviting guests
- [ ] Add static code analysis (PEP8)
- [ ] Add minimum security (server generated token sent in email links instead of player id)
- [ ] Send email notifications to joining/leaving players too, and to players inviting guests
- [ ] Cancel matches (notify players and save stats)
- [ ] Delete player (save stats)
- [ ] Edit match time and place (notify players)
- [ ] Store player first and last names separately. Use first name only when appropriate (in emails for example)
- [ ] Improve error handling
- [ ] Save stats of players leaving matches
- [ ] RESTful URLs and HTTP verbs
- [ ] Encourage players to join an upcoming match if needed
