#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

from datetime import datetime
import csv
import os
import requests
import time


def request(url, headers=None):
    agent = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }
    if headers:
        # py3.5
        headers = {**agent, **headers}
    else:
        headers = agent
    try:
        print('[+] ' + url)
        resp = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        return resp
    except Exception as e:
        print('[-] ERROR >> {}: {}'.format(url, str(e)))
        return False


def write_csv(csv_fname, data, folder=None):
    folder = folder if folder else './'
    try:
        with open(os.path.join(folder, csv_fname), 'a') as f:
            writer = csv.writer(f)
            for d in data:
                writer.writerow([e for e in d])
                f.flush()
    except Exception as e:
        print('[-] CSV ERROR: ', str(e))


def generate_filename(fname):
    return fname + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%I-%M')
