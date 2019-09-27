from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException

class WebDriver:

    def __init__(self, maximize=True):
        self._driver = webdriver.Chrome()
        self._wait = WebDriverWait(self._driver, 2)
    
        if maximize:
            self._driver.maximize_window()
    
    def close(self):
        self._driver.close()

    def get(self, url):
        self._driver.get(url)

    def elem_exists_by_css_selector(self, css_selector):
        try:
            self._driver.find_element_by_css_selector(css_selector)
        except NoSuchElementException:
            return False
        return True

    def click_elem_by_css_selector(self, css_selector):
        self._wait.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
        elem = self._driver.find_element_by_css_selector(css_selector)
        elem.click()

    def send_keys_by_id(self, elem_id, keys):
        self._wait.until(
            ec.element_to_be_clickable((By.ID, elem_id))
        )
        elem = self._driver.find_element_by_id(elem_id)
        elem.send_keys(keys)

    def submit_by_id(self, elem_id):
        elem = self._driver.find_element_by_id(elem_id)
        elem.submit()

    def wait_until_clickable_by_id(self, elem_id):
        self._wait.until(
            ec.element_to_be_clickable((By.ID, elem_id))
        )

    def map_elements_by_css_selector(self, css_selector, func):
        elems = self._driver.find_elements_by_css_selector(css_selector)
        for elem in elems:
            func(elem)
    
    def get_elements_by_css_selector(self, css_selector):
        elems = self._driver.find_elements_by_css_selector(css_selector)
        return elems
    
    def map_elements_by_id(self, elem_id, func):
        elems = self._driver.find_elements_by_id(elem_id)
        for elem in elems:
            func(elem)

    def get_elem_text_by_css_selector(self, css_selector):
        try:
            self._wait.until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )
            elem = self._driver.find_element_by_css_selector(css_selector)
        finally:
            return None if elem is None else elem.text
