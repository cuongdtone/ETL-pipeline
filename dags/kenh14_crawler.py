from datetime import datetime
import os
import airflow
from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator


IMAGE = f"cuongtran73d1/airflow:env"
KENH14 = 'BaoDienTu/kenh14/main.py'


task_args = {
    "depends_on_past": False,
    "email_on_failure": True,
    "owner": "Cuong Tran",
    "email": ["cuonytran@gmail.com"],
}

dag = DAG(
    "etl_pipeline",
    default_args=task_args,
    description="Run crawler",
    start_date=datetime(2023, 2, 7),
    schedule_interval='30 13 * * 0',
    catchup=False
)

tasks = {}

kickoff = DummyOperator(
    task_id='kickoff',
    dag=dag,
)

task_id = "kenh14-crawler"
tasks[task_id] = KubernetesPodOperator(
    dag=dag,
    namespace="airflow",
    image=IMAGE,
    env_vars={
        "PYTHON_SCRIPT_NAME": KENH14
    },
    labels={"app": dag.dag_id},
    name=task_id,
    in_cluster=True,
    task_id=task_id,
    get_logs=True,
)

kickoff >> tasks['kenh14-crawler']
