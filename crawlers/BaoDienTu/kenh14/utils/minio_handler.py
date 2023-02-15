# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 2/13/2023

# minio_handler.py

import time
import os
import random
from datetime import datetime, timedelta

from minio import Minio


class MinioHandler:
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if not MinioHandler.__instance:
            MinioHandler.__instance = MinioHandler()
        return MinioHandler.__instance

    def __init__(self):
        self.minio_url = os.getenv('MINIO_URL')
        self.access_key = os.getenv('MINIO_ACCESS_KEY')
        self.secret_key = os.getenv('MINIO_SECRET_KEY')
        self.bucket_name = os.getenv('MINIO_BUCKET_NAME')
        self.client = Minio(
            self.minio_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )
        self.make_bucket()

    def make_bucket(self) -> str:
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
        return self.bucket_name

    def presigned_get_object(self, bucket_name, object_name):
        # Request URL expired after 7 days
        url = self.client.presigned_get_object(
            bucket_name=bucket_name,
            object_name=object_name,
            expires=timedelta(days=7)
        )
        return url

    def check_file_name_exists(self, bucket_name, file_name):
        try:
            self.client.stat_object(bucket_name=bucket_name, object_name=file_name)
            return True
        except Exception as e:
            print(f'[x] Exception: {e}')
            return False

    def put_object(self, file_data, file_name, content_type):
        try:
            datetime_prefix = time.time()
            object_name = f"{file_name}"
            while self.check_file_name_exists(bucket_name=self.bucket_name, file_name=object_name):
                random_prefix = random.randint(1, 1000)
                object_name = f"{datetime_prefix}_{random_prefix}_{file_name}"

            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                content_type=content_type,
                length=-1,
                part_size=10 * 1024 * 1024
            )
            url = self.presigned_get_object(bucket_name=self.bucket_name, object_name=object_name)
            data_file = {
                'bucket_name': self.bucket_name,
                'file_name': object_name,
                'url': url
            }
            return data_file
        except Exception as e:
            print(e)
