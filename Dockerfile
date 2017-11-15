FROM python:3.6-alpine

MAINTAINER Nick Pleatsikas <nick@pleatsikas.me>

# Copy all files to /opt/ucr-food and set working directory.
COPY . /opt/ucr-food
WORKDIR /opt/ucr-food

# Install required packages.
RUN apk add --update --no-cache \
	g++ gcc libxslt-dev \
	&& pip install -r requirements.txt
