######
# Build stage
############################################
FROM python:3.14-slim-bookworm AS builder

ENV PYTHONUNBUFFERED=1

RUN echo "deb http://deb.debian.org/debian trixie contrib" > /etc/apt/sources.list.d/contrib.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends locales \
    && sed -i 's/^# pt_BR.UTF-8 UTF-8$/pt_BR.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=pt_BR.UTF-8 LC_ALL=pt_BR.UTF-8 \
    && locale -a \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* \
    && useradd app \
    && mkdir -p /app/static \
    && chown -R app:app /app/static \
    && pip install --upgrade --no-cache-dir 'uv'

COPY src/requirements.txt /requirements.txt
RUN uv pip install --system -r /requirements.txt
    

######
# Production stage
############################################
FROM builder AS production

ENV PYTHONUNBUFFERED=1

COPY src/ /app/src/

WORKDIR /app/src
# Garante permissões corretas para cache do uv
RUN mkdir -p /home/app/.cache/uv && chown -R app:app /home/app/.cache
ENV DJANGO_SETTINGS_MODULE=processo_seletivo.settings \
    SECRET_KEY=dummy \
    DEBUG=False
RUN python manage.py collectstatic --noinput --verbosity 2

WORKDIR /app/src
USER app
EXPOSE 8000
ENTRYPOINT ["/app/src/django-entrypoint.sh"]
CMD ["gunicorn"]


######
# Developer stage
############################################
FROM builder AS developer

ENV PYTHONUNBUFFERED=1

COPY src/requirements-dev.txt /requirements-dev.txt
RUN uv pip install --system -r /requirements-dev.txt

WORKDIR /app/src
RUN mkdir -p /home/app/.cache/uv && chown -R app:app /home/app/.cache
USER app
EXPOSE 8000
ENTRYPOINT ["/app/src/django-entrypoint.sh"]
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
