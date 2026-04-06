#!/usr/bin/env bash
set -e

case "${1#-}" in
    gunicorn|python3|python)
        python3 manage.py migrate
        # celery -A processo_seletivo worker -l info &
        # celery -A processo_seletivo beat -l info &
        # celery -A processo_seletivo flower -l info &
        ;;
    *)
        ;;
esac
echo "Starting with command: $*"
exec "$@"