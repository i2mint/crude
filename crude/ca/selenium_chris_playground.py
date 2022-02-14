import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

DFLT_URL = 'http://localhost:8501'
DFLT_DRIVER = webdriver.Chrome


def start(url=DFLT_URL,
          driver=DFLT_DRIVER,
          pause_sec=5):

    # get the driver for the browser
    driver = driver()
    # go to the url
    driver.get(url)
    # wait a bit to give the user the chance to witness the start
    time.sleep(pause_sec)
    return driver


def te_chris(url=DFLT_URL,
             driver=DFLT_DRIVER):

    print('START SELENIUM TEST')
    print('RUN SELENIUM TEST')
    driver = start(url=DFLT_URL,
                   driver=DFLT_DRIVER)

    driver.find_element(By.CSS_SELECTOR, ".element-container:nth-child(2) .st-ci .st-ci").click()
    driver.find_element(By.CSS_SELECTOR, ".element-container:nth-child(2) .st-ci .st-ci").send_keys("1.00")
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, ".element-container:nth-child(3) .st-ci .st-ci").click()
    driver.find_element(By.CSS_SELECTOR, ".element-container:nth-child(3) .st-ci .st-ci").send_keys("24")
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, ".css-ns78wr").click()
    time.sleep(1)
    print('SELENIUM TEST DONE')
    driver.quit()

import streamlit.bootstrap
from importlib_resources import files   # pip install importlib-resources


def start_app():

    t = files('crude')
    app_path = t.joinpath('ca/chris_playground.py')
    streamlit.bootstrap.run(app_path, command_line='', args=[], flag_options={})

if __name__ == "__main__":

    from py2http.util import run_process
    with run_process(func=start_app, is_ready=0, verbose=True):
        te_chris()

