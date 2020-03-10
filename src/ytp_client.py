import getpass
import hashlib
import os
import time
import datetime
import traceback
import re

from bs4 import BeautifulSoup

from src import webdriver as wd
from src.utils import b64_decode, say, safe_make_dir, list_files, write_to_csv, send_email
from src.ytp_constants import HOME_URL, PORTFOLIO_URL, TRANSACTIONS_URL


home_url = 'https://www.yotepresto.com'
requisition_url = f'{home_url}/user/requisitions_listings'


class YTPClient():  
  
    def __init__(self, credentials = None):
        self._has_authed = False
        self._driver = None
        self._credentials = credentials

    def __del__(self):
        try:
            if self._driver:
                self._driver.close()
                self._driver = None
        except Exception:
            pass

    def _require_auth(self):
        if self._has_authed:
            return

        if self._driver is None:
            self._driver = wd.WebDriver()

        self._driver.get(HOME_URL)
        self._driver.click_elem_by_css_selector('#sign-in-button')
        self._driver.wait_until_clickable_by_id('sessions_email')
        self._driver.wait_until_clickable_by_id('sessions_password')

        if self._credentials:
            username, password = self._credentials
            self._username = username
            self._password = password
        else:
            self._username = input('Username: ')
            self._password = getpass.getpass('Password: ')

        invalid_credentials = not (self._username and self._password)
        if invalid_credentials:
            raise Exception('Invalid credentials provided!')

        say('Logging in!')

        self._driver.send_keys_by_id('sessions_email', self._username)
        self._driver.send_keys_by_id('sessions_password', self._password)
        self._driver.submit_by_id('sessions_password')
        self._driver.wait_until_clickable_by_id('sessions_password')
        self._driver.wait_until_clickable_by_selector("a[href='/user/portfolio']")
        say('Logged in!')
        time.sleep(2)
        self._has_authed = True

    def dump_portfolio(self, data_dir):
        self._require_auth()
        self._driver.get(PORTFOLIO_URL)
        portfolio_data_dir = self._get_data_dir(data_dir, 'portfolio')
        safe_make_dir(portfolio_data_dir)
        
        page_num = 1
        
        next_page_selector = "li[class^='page-item next']"
        while True:
            # Wait for the page to load
            self._driver.wait_until_clickable_by_selector(next_page_selector)

            # Save page dump
            file_path = os.path.join(portfolio_data_dir, f'portfolio_{page_num}.html')
            with open(file_path, 'w') as fp:
                page_source = self._driver.get_page_source()
                fp.write(page_source)

            # Check if next page element is disabled
            elem = self._driver.get_element_by_css_selector(next_page_selector)
            attributes = set(list(map(str.lower, elem.get_attribute("class").split())))
            a_elem = elem.find_element_by_css_selector('a')
            print('Downloaded page:', page_num)

            if 'disabled' in attributes or not a_elem:
                break
            self._driver.click(a_elem)
            time.sleep(2)
            page_num += 1

    def _get_data_dir(self, data_dir, sub_dir):
        return os.path.join(data_dir, sub_dir)

    def dump_transactions(self, data_dir):
        self._require_auth()
        self._driver.get(TRANSACTIONS_URL)
        transactions_data_dir = self._get_data_dir(data_dir, 'transactions')
        safe_make_dir(transactions_data_dir)

        page_num = 1
        
        next_page_selector = "li[class^='page-item next']"
        last_page_source_hash = None
        while True:
            # Wait for the page to load
            self._driver.wait_until_clickable_by_selector(next_page_selector)

            # Save page dump
            file_path = os.path.join(transactions_data_dir, f'transactions_{page_num}.html')
            with open(file_path, 'w') as fp:
                page_source = self._driver.get_page_source()
                fp.write(page_source)

            # Check if next page element is disabled
            elem = self._driver.get_element_by_css_selector(next_page_selector)
            attributes = set(list(map(str.lower, elem.get_attribute("class").split())))
            a_elem = elem.find_element_by_css_selector('a')
            print('Downloaded page:', page_num)

            if 'disabled' in attributes or not a_elem:
                break

            self._driver.click(a_elem)

            while True:
                time.sleep(2)
                page_source = self._driver.get_page_source()
                current_page_source_hash = hashlib.md5(page_source.encode('utf-8'))
                if (
                    last_page_source_hash is None or
                    last_page_source_hash != current_page_source_hash
                ):
                    last_page_source_hash = current_page_source_hash
                    break

            page_num += 1

    def extract_portfolio_to_csv(self, data_dir):
        portfolio_data_dir = self._get_data_dir(data_dir, 'portfolio')
        data_header = "table[class='table portfolio'] thead tr td"
        data_row = "table[class='table portfolio'] tbody tr"
        row_data = []
        for f in list_files(portfolio_data_dir, '*.html'):
            with open(f, 'r') as fp:
                html = fp.read()
                soup = BeautifulSoup(html, "html.parser")

            if soup:
                headers = []
                for item in soup.select(data_header):
                    headers.append(item.text.strip())

                rows = soup.select(data_row)
                for row in rows:
                    data = dict()
                    for index, cell in enumerate(row.select('td')):
                        data[headers[index]] = cell.text.strip()
                    row_data.append(data)

        print('Num rows:', len(row_data))
        
        # Normalize and export
        records = []
        for row in row_data:
            row['ID'] = int(row['ID'])
            row['Prestado'] = self._norm_money(row['Prestado'])
            row['Pagado'] = self._norm_money(row['Pagado'])
            row['Te debe'] = self._norm_money(row['Te debe'])

            balance = self._norm_money(row.get('balance', '0'))
            record = tuple(row[header] for header in headers)
            records.append(record)

        headers = tuple(map(str.upper, headers))
        records.sort(key=lambda r: r[0])
        write_to_csv(records, './data/portfolio.csv', headers=headers)

    def _norm_money(self, string: str) -> float:
        return float(string.strip().replace('$',  '').replace(',', '').strip())

    def extract_transactions_to_csv(self, data_dir):
        transactions_data_dir = self._get_data_dir(data_dir, 'transactions')
        data_row = "tr[class^='account_statements']"
        fields = {
            'record_id': ('aut', 'span'),
            'date': ('date', ''),
            'time': ('date', 'span'),
            'reference': ('reference', 'span'),
            'type': ('type', ''),
            'amount': ('amount', ''),
            'balance': ('balance', ''),
        }

        records = []
        for f in list_files(transactions_data_dir, '*.html'):
            with open(f, 'r') as fp:
                html = fp.read()
                soup = BeautifulSoup(html, "html.parser")

            if soup:
                row_data = list()
                for item in soup.select(data_row):
                    data = dict()
                    for data_key, selector_data in fields.items():
                        css_class, sub_elem = selector_data
                        selector = f"td[class='{css_class}']"
                        if sub_elem:
                            selector += f' {sub_elem}'
                        
                        elem = item.select(selector)
                        if isinstance(elem, list):
                            elem = elem[0]

                        if elem and elem.text:
                            text = ' '.join(elem.text.strip().split())
                        else:
                            text = ''

                        data[data_key] = text
                    row_data.append(data)
                
                for row in row_data:
                    record_id = row.get('record_id', '')
                    assert record_id
                    date = row.get('date', '').split()[0]
                    date = datetime.datetime.strptime(date, "%d/%m/%Y").strftime('%Y-%m-%d')

                    time = row.get('time', '').lower()
                    twenty_four_hour_time = time[:4]  # remove the am/pm
                    hour = int(twenty_four_hour_time.split(':')[0])
                    minute = int(twenty_four_hour_time.split(':')[1])

                    is_pm = time[4].lower() == 'p'
                    if is_pm:
                        hour = (hour + 12) % 24

                    time = f'{str(hour).zfill(2)}:{str(minute).zfill(2)}'

                    reference = row.get('reference', '')
                    type_ = row.get('type', '').lower()
                    amount = self._norm_money(row.get('amount', '0'))
                    balance = self._norm_money(row.get('balance', '0'))
                    record = (
                        record_id,
                        date,
                        time,
                        reference,
                        type_,
                        amount,
                        balance,
                    )
                    records.append(record)

        headers = ('ID', 'DATE', 'TIME', 'REFERENCE', 'TYPE', 'AMOUNT', 'BALANCE')
        records.sort(key=lambda r: (r[1], r[2]))
        write_to_csv(records, './data/transactions.csv', headers=headers)

    def loop_purchase_unloaned_requisitions(self):
        num_failures = 0
        max_failures = 3

        def auth_and_clear_existing_orders():
            self._require_auth()

            say('Clearing previous orders')
            self._clear_existing_orders()

        auth_and_clear_existing_orders()

        while num_failures < max_failures:
            try:
                self._has_authed = self._is_authenticated()
                if not self._has_authed:
                    print('Session expired... Re-authenticating...')
                    time.sleep(2)
                    auth_and_clear_existing_orders()

                self._purchase_unloaned_requisitions()

            except Exception as e:
                num_failures += 1
                print('EXCEPTION THROWN:')
                print(str(e))
                traceback.print_exc()

    def _is_authenticated(self) -> bool:
        if not self._driver:
            self._require_auth()

        page_source = self._driver.get_page_source()
        expired_session_message = (
            'Tu sesión ha expirado. Por favor, inicia sesión de nuevo.'
        )
        for found_instance in re.finditer(expired_session_message, page_source):
            return False

        return True

    def _purchase_unloaned_requisitions(self):
        self._get_requisition_page()

        def get_available_spend():
            available_spend_elem = self._driver.get_elem_text_by_css_selector('[class=available]')
            if available_spend_elem is None:
                return 0
            available_spend_string = available_spend_elem.strip()
            if available_spend_string is None:
                return

            available_spend = self._norm_money(available_spend_string)
            if available_spend:
                return available_spend

            return 0

        def add_loan_to_cart(requisition_table_row, loan_amount) -> bool:

            def has_loaned_before(table_row) -> bool:
                row_id_value = table_row.get_attribute('id')
                requisition_id = row_id_value.split('requistion-')[-1]
                row_class_value = table_row.get_attribute('class')
                class_values = row_class_value.strip().split()
                row_data_content_value = table_row.get_attribute('data-content')
                # TODO: Investtigate why sometimes None
                has_loaned_in_data_content_values = False
                if row_data_content_value is not None:
                    data_content_values = row_data_content_value.strip()
                    has_loaned_in_data_content_values = row_data_content_value.startswith('Ya le prestaste')
                has_loaned_in_class_values = 'yalep' in class_values
                return has_loaned_in_class_values or has_loaned_in_data_content_values

            def add_loan() -> bool:
                column_class_attribute_mapping = {
                    'id': 'id',
                    'borrower': 'borrower hidden-xs',
                    'calif': 'calif',
                    'rate': 'rate',
                    'amount': 'amount',
                    'purpose': 'purpose hidden-xs',
                    'term': 'term',
                    'pesos_to_fund': 'hidden-xs hidden-sm',
                    'days_to_fund': 'left hidden-xs hidden-sm',
                }
                row_info = dict()
                for k, v in column_class_attribute_mapping.items():
                    selector = 'td[class="' + v + '"]'
                    column_elem = requisition_table_row.find_element_by_css_selector(
                        selector
                    )
                    if column_elem:
                        col_text = column_elem.text
                        row_info[k] = col_text

                print(row_info)

                row_info['term'] = int(row_info['term'].strip())
                row_info['pesos_to_fund'] = self._norm_money(row_info['pesos_to_fund'])
                row_info['amount'] = self._norm_money(row_info['amount'])
                if row_info['pesos_to_fund'] < loan_amount:
                    return False

                loan_amount_input = (
                    requisition_table_row.find_element_by_css_selector(
                        'input[id^=amount-][inputmode=numeric]'
                    )
                )
                loan_amount_input.click()
                loan_amount_input.send_keys(str(loan_amount))
                loan_amount_input.submit()
                say(f'Added {loan_amount} pesos to cart')

                return True

            has_not_loaned_before = not has_loaned_before(requisition_table_row)
            if has_not_loaned_before:
                return add_loan()
            
            return False

        def _send_email_alert(receipient, amount_left_to_spend):
            send_email(
                receipient=receipient,
                subject=f'YTP: Funds Left (${amount_left_to_spend})',
                body=f'YTP Automation: left ${amount_left_to_spend}',
            )

        req_rows = self._driver.get_elements_by_css_selector(
            'tr[class~=req-item][id^=requisition-]'
        )

        future_available_spend = get_available_spend()
        amount_per_loan = 200
        loaned_amount = 0
        need_to_send_email = False
        for req_row in req_rows:
            if future_available_spend >= amount_per_loan:
                num_thousands = future_available_spend // 1000
                successfully_added_to_cart = add_loan_to_cart(req_row, amount_per_loan)
                if successfully_added_to_cart:
                    future_available_spend -= amount_per_loan
                    loaned_amount += amount_per_loan
                    if num_thousands != future_available_spend // 1000:
                        need_to_send_email = True

        if need_to_send_email:
            _send_email_alert(self._username, future_available_spend)

        time.sleep(2)

        def checkout():
            auth_trigger_button_css_selector = 'button[id=auth_trigger]'
            if self._driver.elem_exists_by_css_selector(auth_trigger_button_css_selector):
                self._driver.click_elem_by_css_selector(auth_trigger_button_css_selector)
                self._driver.send_keys_by_id('ticket_password', self._password)

                def submit_auth(form_elem):
                    input_elem = form_elem.find_element_by_css_selector(
                        'input[type=submit][name=commit][value=Autorizar]'
                    )
                    input_elem.click()

                self._driver.map_elements_by_css_selector(
                    "form[action='/user/tickets/approve']", submit_auth
                )
                say(f'Loaned out {loaned_amount} pesos!')
                time.sleep(2)
                say(f'{future_available_spend} pesos available to loan out!')
                time.sleep(2)

        if loaned_amount > 0:
            checkout()

    def _clear_existing_orders(self):
        self._driver.get(requisition_url)
        time.sleep(2)

        def cancel_order_row(ticket_row):
            ticket_id = ticket_row.get_attribute('id').split('ticket-')[-1]
            form_elem = ticket_row.find_element_by_id(ticket_id)
            eliminate_input = form_elem.find_element_by_css_selector(
                'input[class=eliminar][type=submit]'
            )
            eliminate_input.submit()
            time.sleep(2)

        order_row_css_selector = 'tr[class=ticket-row][id^=ticket-]'
        order_row_exists = self._driver.elem_exists_by_css_selector(order_row_css_selector)
        while order_row_exists:
            order_row = self._driver.get_element_by_css_selector(order_row_css_selector)
            cancel_order_row(order_row)
            order_row_exists = self._driver.elem_exists_by_css_selector(order_row_css_selector)

        time.sleep(2)

    def _get_requisition_page(self):
        self._driver.get(requisition_url)
        time.sleep(2)
