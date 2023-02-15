from kubernetes.client import models as k8s

import logging
import os

import pendulum

from airflow import DAG
from airflow.configuration import conf
from airflow.decorators import task
from airflow.example_dags.libs.helper import print_stuff


with DAG(
    dag_id='kenh14_crawler',
    schedule_interval='43 8 * * *',
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=['crawler'],
    ) as dag:


    executor_config_crawler = {
        "pod_override": k8s.V1Pod(
            spec=k8s.V1PodSpec(
                containers=[
                    k8s.V1Container(
                        name="base",
                    ),
                    k8s.V1Container(
                        name="sidecar",
                        image="cuongtran73d1/airflow:env",
                        args=["python /crawlers/BaoDienTu/kenh14/main.py"],
                        command=["bash", "-cx"],
                        env=[
                            k8s.V1EnvVar(name="PROD", value='TRUE'), 
                            k8s.V1EnvVar(name="DOMAIN", value='https://kenh14.vn/'), 
                            # k8s.V1EnvVar(name="KAFKA_BOOTSTRAP_SERVER", value='192.168.1.161:9092'), 
                            # k8s.V1EnvVar(name="KAFKA_TOPIC", value='news'), 
                            k8s.V1EnvVar(name="MONGO_URI", value='192.168.1.161:27017'), 
                            k8s.V1EnvVar(name="MONGO_DB", value='CrawlerDataDB'), 
                        ]
                    ),
                ], 
            )
        ),
    }

    @task(executor_config=executor_config_crawler)
    def crawl_task():
        print_stuff()

    crawl = crawl_task()