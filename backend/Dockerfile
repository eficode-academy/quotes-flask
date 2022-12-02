FROM python:3.10-alpine

COPY requirements.txt /app/

WORKDIR /app

# we need a bunch dependencies to build the psycopg2 package, but we don't them need to run it afterwards
RUN \
    apk add --no-cache --virtual .build gcc python3-dev musl-dev postgresql-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del --no-cache .build

# install library needed for postgres interface
RUN apk add --no-cache postgresql-libs

COPY . /app

EXPOSE 5000

# start gunicorn in front of flask python processes
# this will start gunicorn with 4 worker processes
CMD ["gunicorn", "-w 4", "-b", "0.0.0.0:5000", "app:app"]
