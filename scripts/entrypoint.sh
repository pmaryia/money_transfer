echo 'Running migrations...'
poetry run python -m manage migrate

echo 'Collecting static files...'
poetry run python -m manage collectstatic --noinput

echo 'Creating fake users...'
poetry run python -m manage create_fake_users

echo 'Starting uwsgi...'
poetry run uwsgi --ini uwsgi.ini
