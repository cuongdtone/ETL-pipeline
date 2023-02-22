
##################### dev env
import os
if os.getenv('ENV') != 'PROD':
    from env_dev import set_dev_env
    set_dev_env()
#####################

import crawl


if __name__ == "__main__":
    crawl.start_crawl(mode='old', recent_date='14/02/2023', end_date='13/02/2023', recent_page=60)
