FROM python:3.10-alpine
RUN \
    apk add --no-cache curl bash

COPY requirements.txt /app/

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000

ARG VERSION=1.0.0
ENV APP_VERSION=${VERSION}

# start gunicorn in front of flask python processes
# this will start gunicorn with 4 worker processes
CMD ["gunicorn", "-w 4", "-b", "0.0.0.0:5000", "app:APP"]
