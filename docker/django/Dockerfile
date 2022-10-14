ARG PYTHON_VERSION=3.9-slim-bullseye



# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} as python

# Python build stage
FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=production

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
    # dependencies for building Python packages
    build-essential \
    # psycopg2 dependencies
    libpq-dev

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt .

# Create Python Dependency and Sub-Dependency Wheels.
RUN pip wheel --wheel-dir /usr/src/app/wheels  \
    -r requirements.txt


# Python 'run' stage
FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=production
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

RUN addgroup --system django \
    && adduser --system --ingroup django django


# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    # psycopg2 dependencies
    libpq-dev \
    # Postgres dependencies
    postgresql-client \
    # Translations dependencies
    gettext \
    # cleaning up unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/


COPY --chown=django:django ./docker/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint


COPY --chown=django:django ./docker/django/start-local /start-local
RUN sed -i 's/\r$//g' /start-local
RUN chmod +x /start-local

COPY --chown=django:django ./docker/django/start-production /start-production
RUN sed -i 's/\r$//g' /start-production
RUN chmod +x /start-production


COPY --chown=django:django ./docker/django/celery/worker/start-local /start-local-celeryworker
RUN sed -i 's/\r$//g' /start-local-celeryworker
RUN chmod +x /start-local-celeryworker


COPY --chown=django:django ./docker/django/celery/worker/start-production /start-production-celeryworker
RUN sed -i 's/\r$//g' /start-production-celeryworker
RUN chmod +x /start-production-celeryworker

# copy application code to WORKDIR
COPY --chown=django:django . ${APP_HOME}

# make django owner of the WORKDIR directory as well.
RUN chown django:django ${APP_HOME}

USER django
EXPOSE 6200
ENTRYPOINT ["/entrypoint"]