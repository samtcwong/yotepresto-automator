import base64
import csv
import glob
import os
import subprocess
import requests

from typing import List, Any, Optional
from pathlib import Path


def say(text, debug=False):
    if debug or True:
        print(text)
        process = subprocess.Popen(
            ['say', '-v', 'Samantha', text],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

def b64_decode(string):
    bytes_ = bytes(string, 'utf-8')
    return base64.decodestring(bytes_).decode('utf-8').rstrip()


def safe_make_dir(dir: str) -> None:
    Path(dir).mkdir(parents=True, exist_ok=True)


def list_files(dir: str, pattern: str) -> None:
    glob_pattern = os.path.join(dir, pattern)
    yield from glob.iglob(glob_pattern)


def write_to_csv(tuples: List[Any], filepath: str, headers: Optional[List[Any]] = None) -> None:
    with open(filepath,'w') as fp:
        csv_writer = csv.writer(fp)
        if headers:
            csv_writer.writerow(headers)
        csv_writer.writerows(tuples)


def send_email(receipient, subject, body):
    GOOGLE_APP_SCRIPT_ID = os.environ.get('EMAIL_SERVICE_GOOGLE_APP_SCRIPT_APP_ID')
    EMAIL_SERVICE_URI = f'https://script.google.com/macros/s/{GOOGLE_APP_SCRIPT_ID}/exec'
    SECRET = os.environ.get('EMAIL_SERVICE_GOOGLE_APP_SCRIPT_SECRET')
    r = requests.post(
        EMAIL_SERVICE_URI,
        data={
            'secret': SECRET,
            'receipient': receipient,
            'subject': subject,
            'body': body,
        }
    )

    if r.status_code != 200:
        print(f'ERROR: {r.content}')
