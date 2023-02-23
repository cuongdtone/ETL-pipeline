# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 2/13/2023

import os
from selenium import webdriver


def get_selenium_driver():
    SELENIUM_OP = os.getenv('SELENIUM_OP')
    SELENIUM_TYPE = os.getenv('SELENIUM_TYPE')
    SELENIUM_HUB = os.getenv('SELENIUM_HUB')

    if SELENIUM_TYPE == 'grid':
        if SELENIUM_OP == "CHROME":
            options = webdriver.ChromeOptions()
        elif SELENIUM_OP == "FIREFOX":
            options = webdriver.FirefoxOptions()
        else:
            options = webdriver.ChromeOptions()

        driver = webdriver.Remote(
            command_executor=SELENIUM_HUB,
            options=options
        )
        return driver
    else:
        from webdriver_manager.chrome import ChromeDriverManager
        driver = webdriver.Chrome(ChromeDriverManager().install())
        return driver
