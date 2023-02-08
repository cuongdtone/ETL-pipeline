FROM python:3.6-slim


# install deps
RUN apt-get update -y && apt-get install -y \
    libczmq-dev \
    libssl-dev \
    inetutils-telnet \
    bind9utils \
    gcc \
    && apt-get clean

RUN pip install --upgrade pip


RUN pip install apache-airflow==1.10.10
RUN pip install 'apache-airflow[kubernetes]'
RUN pip install 'apache-airflow[postgres]'
RUN pip install wtforms==2.3.3
RUN pip install SQLAlchemy==1.3.23 
RUN pip install Flask-SQLAlchemy==2.4.4

# COPY requirements.txt /requirements.txt
# RUN pip install -r /requirements.txt
RUN #rm -rf /root/airflow/dags

COPY airflow-test-env-init.sh /tmp/airflow-test-env-init.sh


COPY bootstrap.sh /bootstrap.sh
RUN chmod +x /bootstrap.sh
ENTRYPOINT ["/bootstrap.sh"]
