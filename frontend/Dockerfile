FROM python:3.10-alpine

COPY requirements.txt /app/

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000

# start gunicorn in front of flask python processes
# this will start gunicorn with 4 worker processes
CMD ["gunicorn", "-w 4", "-b", "0.0.0.0:5000", "app:app"]
