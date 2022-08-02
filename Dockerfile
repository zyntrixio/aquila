FROM ghcr.io/binkhq/python:3.10 as build

WORKDIR /src

RUN apt-get update && apt-get install -y git
RUN pip install poetry==1.2.0b3
RUN poetry config virtualenvs.create false
RUN pip install poetry-dynamic-versioning-plugin    

ADD . .
RUN poetry build

FROM ghcr.io/binkhq/python:3.10
ARG wheel=aquila-*-py3-none-any.whl

WORKDIR /app
COPY --from=build /src/dist/$wheel .
COPY --from=build /src/wsgi.py .
RUN pip install $wheel && rm $wheel

ENTRYPOINT [ "linkerd-await", "--" ]
CMD [ "gunicorn", "--workers=2", "--threads=2", "--error-logfile=-", \
    "--access-logfile=-", "--bind=0.0.0.0:9000", "--bind=0.0.0.0:9100", "wsgi:app" ]