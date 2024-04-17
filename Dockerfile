FROM ghcr.io/binkhq/python:3.11
ARG PIP_INDEX_URL
ARG APP_NAME
ARG APP_VERSION
WORKDIR /app
RUN pip install --no-cache ${APP_NAME}==$(echo ${APP_VERSION} | cut -c 2-)
ADD wsgi.py .

ENV PROMETHEUS_MULTIPROC_DIR=/dev/shm
CMD [ "gunicorn", "--workers=2", "--threads=2", "--error-logfile=-", \
    "--access-logfile=-", "--bind=0.0.0.0:9000", "--bind=0.0.0.0:9100", "wsgi:app" ]
