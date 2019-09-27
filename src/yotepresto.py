import base64
import getpass
import os
import random
import re
import subprocess
import time
import traceback

from src import webdriver as wd

from pathlib import Path

home = str(Path.home())

home_url = 'https://www.yotepresto.com'
requisition_url = f'{home_url}/user/requisitions_listings'


def b64_decode(string):
    bytes_ = bytes(string, 'utf-8')
    return base64.decodestring(bytes_).decode('utf-8').rstrip()


def login(driver, username, password):
    say('Logging in! Sound check, 1, 2, 1, 2!')
    driver.get(home_url)
    driver.click_elem_by_css_selector('#sign-in-button')
    driver.wait_until_clickable_by_id('sessions_email')
    driver.wait_until_clickable_by_id('sessions_password')
    driver.send_keys_by_id('sessions_email', username)
    driver.send_keys_by_id('sessions_password', password)
    driver.submit_by_id('sessions_password')
    time.sleep(3)
    say('Logged in!')


def cancel_orders(driver):
    driver.get(requisition_url)
    time.sleep(5)

    def cancel_order_row(ticket_row):
        ticket_id = ticket_row.get_attribute('id').split('ticket-')[-1]
        form_elem = ticket_row.find_element_by_id(ticket_id)
        eliminate_input = form_elem.find_element_by_css_selector(
            'input[class=eliminar][type=submit]'
        )
        eliminate_input.submit()

    driver.map_elements_by_css_selector(
        'tr[class=ticket-row][id^=ticket-]',
        cancel_order_row
    )


def get_requisition_page(driver):
    driver.get(requisition_url)
    time.sleep(2)


def order_unloaned_requisitions(driver):
    cancel_orders(driver)
    get_requisition_page(driver)
    available_spend_string = (
        driver.get_elem_text_by_css_selector('[class=available]').strip()
    )
    if available_spend_string is None:
        return

    available_spend = float(
        available_spend_string.replace('$', '').replace(',', '')
    )

    def loan_out(requisition_table_row, loan_amount):
        row_id_value = requisition_table_row.get_attribute('id')
        requisition_id = row_id_value.split('requistion-')[-1]
        row_class_value = requisition_table_row.get_attribute('class')
        class_values = row_class_value.strip().split()

        if 'yalep' not in class_values:
            loan_amount_input = (
                requisition_table_row.find_element_by_css_selector(
                    'input[id^=amount-][inputmode=numeric]'
                )
            )
            loan_amount_input.click()
            loan_amount_input.send_keys(str(loan_amount))
            loan_amount_input.submit()

    req_rows = driver.get_elements_by_css_selector(
        'tr[class~=req-item][id^=requisition-]'
    )

    amount_per_loan = 200
    loaned_amount = 0
    for req_row in req_rows:
        future_available_spend = available_spend - amount_per_loan
        if future_available_spend >= 0:
            loan_out(req_row, amount_per_loan)
            available_spend -= amount_per_loan
            loaned_amount += amount_per_loan

    time.sleep(3)
    auth_trigger_button_css_selector = 'button[id=auth_trigger]'
    if driver.elem_exists_by_css_selector(auth_trigger_button_css_selector):
        driver.click_elem_by_css_selector(auth_trigger_button_css_selector)
        driver.send_keys_by_id('ticket_password', password)
        def submit_auth(form_elem):
            input_elem = form_elem.find_element_by_css_selector(
                'input[type=submit][name=commit][value=Autorizar]'
            )
            input_elem.click()

        driver.map_elements_by_css_selector(
            "form[action='/user/tickets/approve']", submit_auth
        )
        say(f'Loaned out {loaned_amount} pesos!')
        say(f'{future_available_spend} pesos available to loan out!')
        time.sleep(2)


def say(text, debug=False):
    if debug:
        process = subprocess.Popen(
            ['say', '-v', 'Samantha', text],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )


def main():

    username = input('Username: ')
    password = getpass.getpass('Password: ')

    if not username and not password:
        return

    driver = wd.WebDriver()
    try:
        login(driver, username, password)
        while True:
            order_unloaned_requisitions(driver)
            time.sleep(5)
    except Exception as e:
        say(f'Exception thrown: {e}')
        traceback.print_exc()

    driver.close()
