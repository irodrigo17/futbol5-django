web: gunicorn futbol5.wsgi --log-file -
celery: celery worker --app=core.tasks.app -B
test: ./manage.py test
shell: ./manage.py shell
