#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import numpy as np

## Reminder to check the Chromedriver to match the Chrome browser
## https://chromedriver.chromium.org/downloads
CHROMEDRIVER_PATH = ('./chromedriver.exe')

## Link to CCC Data ##
URL = "https://www.coronavirus.cchealth.org/overview"


def random_wait():
    wait_time = np.random.randint(4, 10)
    print('Waiting for {} seconds'.format(wait_time))
    return time.sleep(wait_time)


def get_data():

        # open instance of Chrome
        driver = webdriver.Chrome(CHROMEDRIVER_PATH)
        driver.get(URL)
        random_wait()

        #define wait times
        wait10 = WebDriverWait(driver, 10)
        wait20 = WebDriverWait(driver, 20)

        # # toggle to iframe, select dowload data by city
        random_wait()
        driver.switch_to.frame('htmlComp-iframe')
        wait10.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="export2"]'))).click()

        random_wait()

        print('Data Successfully Downloaded')
        print('Closing browser...')


if __name__ == '__main__':
    get_data()
