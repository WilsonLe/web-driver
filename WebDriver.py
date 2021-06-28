import os
import sys
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
load_dotenv()


class WebDriver():
    def __init__(self):
        self.TIMEOUT = 60  # seconds
        self.options = Options()
        if os.getenv("PYTHON_ENV") == "production":
            self.options.add_argument('--headless')
        self.driver = None

    def attempt(self, function):
        """A way to avoid try-catch pyramid of doom.
        If input function works, return [return value of function, none]
        If input function fails, return [None, error message]
        Usage:
                value, error = attempt(function)
                if error:
                        print(error)
                # do something with value
        """
        try:
            return function(), None
        except Exception as e:
            return None, e

    def handle_error(self, err):
        self.stop()

    def start(self):
        """Start and open the driver process"""
        self.driver, err = self.attempt(
            lambda: webdriver.Chrome(options=self.options))
        res, err = self.driver, err
        if err:
            raise Exception(err)
        return res

    def stop(self):
        """Stop and close the driver process"""
        return self.driver.close()

    def goto(self, url):
        """Go to the specified URL (should starts with http/https)"""
        if not url.startswith('https://'):
            url = 'https://' + url
        res, err = self.attempt(lambda: self.driver.get(url))
        if err:
            return self.handle_error(err)
        return res

    def query_selector(self, selector):
        """get element by selector
        Return selenium element.
        If selector is ID and XPATH, return single item. If classname, return array of elements.
        """
        res, err = self.attempt(
            lambda: self.driver.find_elements_by_css_selector(selector))
        if err:
            return self.handle_error(err)
        if len(res) == 0:
            err = f'No element with \'{selector}\' query found'
            self.handle_error(err)
        elif len(res) == 1:
            return res[0]
        else:
            return res

    def wait_for(self, selector):
        """wait for element with input selector to present"""
        element_present = EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector))
        res, err = self.attempt(lambda: wait(
            self.driver, self.TIMEOUT).until(element_present))
        if err:
            return self.handle_error(err)
        return res

    def wait_for_and_switch_to_iframe(self, selector):
        """wait for iframe and switch to it"""
        iframe_present = EC.frame_to_be_available_and_switch_to_it(selector)
        res, err = self.attempt(lambda: wait(
            self.driver, self.TIMEOUT).until(iframe_present))
        if err:
            return self.handle_error(err)
        return res

    def switch_default(self):
        """switch driver back to default, main content"""
        return self.driver.switch_to.default_content()
