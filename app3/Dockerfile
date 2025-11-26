FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install flask

RUN mkdir -p /var/log/app3

CMD ["python", "app.py"]
