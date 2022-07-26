FROM ghcr.io/binkhq/python:3.10 as build

WORKDIR /src

RUN pip install poetry==1.2.0b3
RUN poetry config virtualenvs.create false

ADD . .
RUN poetry build

FROM ghcr.io/binkhq/python:3.10

ARG wheel=aquila-0.0.0-py3-none-any.whl

WORKDIR /app
COPY --from=build /src/dist/$wheel .
COPY --from=build /src/wsgi.py .
RUN pip install $wheel && rm $wheel

ENTRYPOINT [ "linkerd-await", "--" ]
CMD [ "gunicorn", "--workers=2", "--threads=2", "--error-logfile=-", \
    "--access-logfile=-", "--bind=0.0.0.0:9000", "wsgi:app" ]