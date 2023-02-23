# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 2/13/2023

import os


def set_env_var(var, value):
    os.environ[var] = value


try:
    if os.getenv('ENV') != 'PROD':
        with open('.env.dev', encoding='utf8') as f:
            variables = f.readlines()
        for kv in variables:
            kv = kv.strip().split('=')
            if len(kv) == 2:
                set_env_var(*kv)
except:
    print('PROD ENV is set')
