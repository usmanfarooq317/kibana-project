FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install flask

RUN mkdir -p /var/log/app1

CMD ["python", "app.py"]
