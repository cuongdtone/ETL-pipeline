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
                        image="cuongtran73d1/crawlers:latest",
                        args=["python /crawlers/BaoDienTu/kenh14/main.py"],
                        command=["bash", "-cx"],
                        env=[
                            k8s.V1EnvVar(name="ENV", value='PROD'),
                            k8s.V1EnvVar(name="DATA_LAKE", value='mongo'),
                            k8s.V1EnvVar(name="DOMAIN", value='https://kenh14.vn/'),
                            k8s.V1EnvVar(name="ARG1", value='new'),

                            k8s.V1EnvVar(name="MONGO_URI", value='192.168.1.159:27017'),
                            k8s.V1EnvVar(name="MONGO_DB", value='CrawlerDataDB'), 
                            k8s.V1EnvVar(name="MONGO_COLLECTION", value='news'),

                            k8s.V1EnvVar(name="MINIO_URL", value='192.168.1.159:9000'),
                            k8s.V1EnvVar(name="MINIO_ACCESS_KEY", value='admin'),
                            k8s.V1EnvVar(name="MINIO_SECRET_KEY", value='password@123'),
                            k8s.V1EnvVar(name="MINIO_BUCKET_NAME", value='images'),
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