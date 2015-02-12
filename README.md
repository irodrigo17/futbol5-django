# Futbol 5

Very basic [Django](https://www.djangoproject.com) app for managing weekly soccer matches.

Basically, it just creates matches every week and emails a join link to players.

Based on the [Futbol 5 Rails app](https://github.com/irodrigo17/fulbol5).

## TODOs

- [x] Create basic match view
- [x] Add tests
- [x] Deploy to [Heroku](https://devcenter.heroku.com/articles/getting-started-with-python)
- [ ] Seed DB with default players
- [ ] Fix timezone warning
- [ ] Create CRON Job to create matches and send emails, check [django-crontab](https://github.com/kraiz/django-crontab)
- [ ] Integrate [TravisCI](https://travis-ci.org/)
- [ ] Cancel matches
- [ ] Invite external friends to a match (not included in future emails by default)
- [ ] Edit match time and place
- [ ] Improve UI
