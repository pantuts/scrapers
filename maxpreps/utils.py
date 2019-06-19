#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import browser_cookie3
import csv
import time
from bs4 import BeautifulSoup
from datetime import datetime


def get_cookies():
    cookies = browser_cookie3.chrome()
    return cookies


def request(s, url, cookies):
    try:
        print('[+] Getting source: {}'.format(url))
        resp = s.get(url, cookies=cookies)
        soup = BeautifulSoup(resp.text, 'lxml')
        return soup
    except Exception as e:
        print('[!] ERROR: {}'.format(e))
        return False


def generate_filename(fname):
    return fname + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%I-%M')


def write_csv(csv_fname, data):
    try:
        with open(csv_fname, 'a') as f:
            writer = csv.writer(f)
            for d in data:
                writer.writerow([e for e in d])
                f.flush()
    except Exception as e:
        print('[-] CSV ERROR: ', str(e))
