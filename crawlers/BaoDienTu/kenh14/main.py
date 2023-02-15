
##################### dev env
import os
if os.getenv('PROD') != 'TRUE':
    from env_dev import set_dev_env
    set_dev_env()
#####################

import crawl

if __name__ == "__main__":
    crawl.start_crawl()
