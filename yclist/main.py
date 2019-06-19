#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import csv
import requests
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_tld


def request(url):
    print('[+] Getting source for: ' + url)
    try:
        agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) '
        agent += 'AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.463.0 Safari/534.3'
        headers = {
            'User-Agent': agent
        }
        req = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(req.text, 'html.parser')
        return soup
    except Exception as e:
        print('[-] ERROR: >> ' + str(e))
        return False


def write_csv(csv_fname, data):
    for d in data:
        with open(csv_fname + '.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([e for e in d])
            f.flush()
    print('[+] Done: ' + data[0][0])


def main():
    soup = request('http://yclist.com')
    if soup:
        csv_fname = 'YCLIST_' + \
            datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %I:%M')
        trs = soup.select('table tbody tr')
        if trs:
            for tr in trs:
                data = []
                for i, td in enumerate(tr.select('td')):
                    if i == 0:
                        continue
                    txt = td.get_text().strip()
                    if len(txt) == 0:
                        txt = 'none'
                    if 'http' in txt:
                        txt = get_tld(txt)
                    data.append(txt)
                write_csv(csv_fname, [data])


if __name__ == '__main__':
    main()
