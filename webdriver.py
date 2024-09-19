from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from seleniumbase import Driver


def driver_confrigration():
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    driver = Driver(uc=True, headless=False)
    # driver = webdriver.Chrome(service=Service(), options=options)
    return driver
