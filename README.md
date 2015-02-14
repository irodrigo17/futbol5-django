# Futbol 5

Very basic [Django](https://www.djangoproject.com) app for managing weekly soccer matches.

Basically, it just creates matches every week and emails a join link to players.

Based on the [Futbol 5 Rails app](https://github.com/irodrigo17/fulbol5).


## Tech stuff

Running on Python 2.7 and Django 1.7 and deployed to [Heroku](https://fobal.herokuapp.com).

Using [PostgreSQL](http://www.postgresql.org) as the database backend.

Sending mails with the [default Django SMTP email backend](https://docs.djangoproject.com/en/1.7/topics/email/).

Can use [Celery](http://www.celeryproject.org) for running scheduled tasks with [RabbitMQ](https://www.rabbitmq.com) as the broker and [Redis](http://redis.io) as the results backend, but it needs a worker dyno running besides de web dyno, and having two dynos is not free on Heroku. So, using the [Temporize Add-On](https://www.temporize.net/) to `GET /sedmail` instead, not as pretty, but it does the trick.

Dependencies can be installed using `pip install`.

Tests can be run with `python manage.py test`.


#### Environment variables

There are some environment variables that need to be set for the app to work properly, namely:

- `DATABASE_URL` - The URL of the the PostgreSQL database, example: `postgres://localhost/fobal`.
- `BROKER_URL` - The URL of the Celery broker, example: `amqp://`.
- `CELERY_RESULT_BACKEND` - The URL for the Celery results backend, example: `redis://localhost`.
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
- [ ] Format and localize match date in emails and views
- [ ] Cancel matches (notify players)
- [ ] Invite external friends to a match (notify players)
- [ ] Edit match time and place (notify players)
- [ ] Leave match link (notify players)
- [ ] Send email notification a day before a match with players list, add optional friend invitations if len(match.players) < 10
- [ ] Store player first and last names separately, and use only first name in emails
- [ ] Integrate [TravisCI](https://travis-ci.org/)
- [ ] Seed DB with default players
- [ ] Remove all celery stuff if the temporize add-on works out
- [ ] Improve UI
