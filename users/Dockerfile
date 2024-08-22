FROM python:3.8.0-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev zlib-dev jpeg-dev dumb-init

COPY . /usr/src/app

ENTRYPOINT ["/usr/bin/dumb-init", "--"]

CMD ["sh", "entrypoint.sh"]