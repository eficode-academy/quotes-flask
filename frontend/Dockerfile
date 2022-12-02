FROM python:3.10-slim
RUN apt-get update && apt-get install -y \
 curl \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000

# start gunicorn in front of flask python processes
# this will start gunicorn with 4 worker processes
CMD ["gunicorn", "-w 4", "-b", "0.0.0.0:5000", "app:app"]
