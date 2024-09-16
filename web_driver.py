
from selenium.webdriver.chrome.options import Options
from seleniumbase import Driver

def initialize_driver():
    print("initialize_driver")
    # print('jkjjkkjjkjk')
     # Set up the Chrome WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    return  Driver(uc=True, headless=False)
