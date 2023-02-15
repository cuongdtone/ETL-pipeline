FROM python:3.8

COPY crawlers/ crawlers/
COPY requirements.txt .
RUN pip install -r requirements.txt