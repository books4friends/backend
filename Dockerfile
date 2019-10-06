FROM alpine

RUN apk update && apk upgrade
RUN apk add --update python3 python3-dev postgresql-client postgresql-dev build-base gettext jpeg-dev zlib-dev && pip3 install --upgrade pip

RUN mkdir -p /app/
WORKDIR /app/
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY . /app/