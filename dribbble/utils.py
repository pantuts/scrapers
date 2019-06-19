#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import csv
import os
import requests
import sys
from urllib.request import urlretrieve


AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) '
AGENT += 'AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.463.0 Safari/534.3'
HEADERS = {'User-Agent': AGENT}


def create_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def request(url):
    print('[+] Getting source: {}'.format(url))
    try:
        resp = requests.get(url, headers=HEADERS)
        return resp
    except Exception:
        return False


def write_csv(data, folder, fname):
    try:
        with open(os.path.join(folder, fname), 'a') as f:
            writer = csv.writer(f)
            for d in data:
                writer.writerow([e for e in d])
                f.flush()
    except Exception as e:
        print(str(e))
        return False


def download(url, folder, fname):
    try:
        def download_progress(counter, bsize, size):
            prog_percent = (counter * bsize * 100) / size
            sys.stdout.write('\r' + fname  + \
                ' .......................... ')
            sys.stdout.flush()
        urlretrieve(url, os.path.join(folder, fname), reporthook=download_progress)
        return True
    except Exception as e:
        print(str(e))
