#!/usr/bin/env bash
# start-server.sh
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (cd mmt-backend; python manage.py createsuperuser --no-input)
fi
(cd mmt-backend; gunicorn mmt_backend_project.wsgi --reload --user www-data --bind unix:/opt/mmt.sock --workers 3) &
nginx -g "daemon off;"
