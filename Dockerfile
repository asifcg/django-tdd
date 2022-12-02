FROM python:3.9-alpine3.13

LABEL maintainer="thecodegenesis.com"

ENV PYTHONBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements-dev.txt /tmp/requirements-dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false

# RUN python -m venv /.venv && \ 
#     /.venv/bin/pip install --upgrade pip && \
#     rm -rf /tmp && \
#     adduser \
#         --disabled-password \
#         --no-create-home \
#         appuser

RUN if [ "$DEV" = "true" ]; \
        then pip3 install -r /tmp/requirements-dev.txt; \ 
        else pip3 install -r /tmp/requirements.txt; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        appuser


USER appuser