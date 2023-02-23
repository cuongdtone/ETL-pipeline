from kubernetes.client import models as k8s
from dags.base_env import env_base
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
                        env=env_base + [
                            k8s.V1EnvVar(name="DOMAIN", value='https://kenh14.vn/'),
                            k8s.V1EnvVar(name="ARG1", value='new')
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

    executor_config_crawler2 = {
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
                        env=env_base + [
                            k8s.V1EnvVar(name="DOMAIN", value='https://kenh14.vn/'),
                            k8s.V1EnvVar(name="ARG1", value='old')
                        ]
                    ),
                ],
            )
        ),
    }

    @task(executor_config=executor_config_crawler2)
    def crawl_task2():
        print_stuff()
    crawl2 = crawl_task2()

    crawl >> crawl2
