import base64
import os
import random
import re
import subprocess
import time
import traceback

from src.utils import b64_decode, say

from pathlib import Path

home = str(Path.home())


def main():
    from src.ytp_client import YTPClient
    ytp_username_hash = os.environ.get('YTP_USERNAME_HASH')
    ytp_password_hash = os.environ.get('YTP_PASSWORD_HASH')

    credentials = None
    if ytp_username_hash and ytp_password_hash:
        ytp_username = b64_decode(ytp_username_hash)
        ytp_password = b64_decode(ytp_password_hash)
        credentials = ytp_username, ytp_password

    client = YTPClient(credentials=credentials)

    # TODO: Add `click` to manage CLI options
    # data_dir = './data'
    # client.dump_portfolio(data_dir)
    # client.dump_transactions(data_dir)
    # client.extract_portfolio_to_csv(data_dir)
    # client.extract_transactions_to_csv(data_dir)
    client.loop_purchase_unloaned_requisitions()
