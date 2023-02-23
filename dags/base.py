# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 2/23/2023


from kubernetes.client import models as k8s

env_base = [
            k8s.V1EnvVar(name="ENV", value='PROD'),
            k8s.V1EnvVar(name="DATA_LAKE", value='mongo'),

            k8s.V1EnvVar(name="MONGO_URI", value='192.168.1.159:27017'),
            k8s.V1EnvVar(name="MONGO_DB", value='CrawlerDataDB'),
            k8s.V1EnvVar(name="MONGO_COLLECTION", value='news'),

            k8s.V1EnvVar(name="MINIO_URL", value='192.168.1.159:9000'),
            k8s.V1EnvVar(name="MINIO_ACCESS_KEY", value='admin'),
            k8s.V1EnvVar(name="MINIO_SECRET_KEY", value='password@123'),
            k8s.V1EnvVar(name="MINIO_BUCKET_NAME", value='images'),
        ]