#define python version
FROM python:3.8-slim


COPY requirements.txt .

RUN apt-get update -y && apt-get install -y \
    libczmq-dev \
    libssl-dev \
    inetutils-telnet \
    bind9utils \
    gcc \
    && apt-get clean

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY crawlers/* crawlers/

ENTRYPOINT python -u crawlers/$PYTHON_SCRIPT_NAME
