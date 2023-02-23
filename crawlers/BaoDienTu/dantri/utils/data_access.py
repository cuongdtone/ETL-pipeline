# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 2/17/2023

import os
from io import BytesIO
import mimetypes
import os


class DataHandler:
    def __init__(self):
        self.data_lake_mode = os.getenv('DATA_LAKE')

        if self.data_lake_mode.lower() == 'mongo':
            from .db_handler import MongoHandler
            self.data_lake = MongoHandler()
        elif self.data_lake_mode.lower() == 'kafka':
            from .kafka_handler import KafkaHandler
            self.data_lake = KafkaHandler()

        #################### file lake
        if os.getenv('MINIO_URL') is not None:
            from .minio_handler import MinioHandler
            self.file_lake = MinioHandler()

    def put(self, item, files=None):
        if files is not None:
            data_files = []
            for file in files:
                try:
                    content_type = mimetypes.MimeTypes().guess_type(file)[0]
                    with open(file, 'rb') as f:
                        data = f.read()
                    data_file = self.file_lake.get_instance().put_object(
                        file_name=os.path.basename(file),
                        file_data=BytesIO(data),
                        content_type=content_type)
                    del data
                    data_files.append(data_file)
                except:
                    pass
            item['files'] = data_files
        print(item)
        self.data_lake.put(item)



