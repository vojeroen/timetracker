FROM python:3.7-slim-buster

RUN set -x && \
    apt-get update && \
    apt-get install -y dumb-init && \
    apt-get clean

COPY requirements.txt /app/requirements.txt

RUN set -x && \
    pip install -r /app/requirements.txt

RUN set -x && \
    mkdir /app/data

COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini
COPY app /app/app
COPY scripts/timetracker.sh /app/timetracker.sh

VOLUME ["/app/data"]

ENTRYPOINT ["dumb-init", "--"]
CMD ["/bin/bash", "/app/timetracker.sh"]
