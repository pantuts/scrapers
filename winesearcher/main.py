#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

'''
This site has strict security so it has to be manually checked during Bot Check
and vpn restart.
'''

from bs4 import BeautifulSoup
from datetime import datetime
from tenacity import retry, stop_after_attempt, stop_after_delay, TryAgain
from user_agents import set_agent
import csv
import notify2
import os
import requests
import sys
import time

REQUEST_SESSION = None
REQUEST_HEADERS = None
REQUEST_SESSION_MAIN_URL_COUNT = 0
REQUEST_SESSION_COUNT = 0
REQUEST_ERROR_COUNT = 0
REQUEST_ERROR_MAX_COUNT = 15


def another_request(url, is_main_url=False):
    global REQUEST_SESSION, REQUEST_ERROR_COUNT

    REQUEST_SESSION.cookies.clear()
    REQUEST_SESSION = None
    REQUEST_ERROR_COUNT = 0

    notify()
    vpn_restarted = 'n'
    while vpn_restarted != 'y':
        vpn_restarted = input('Started? y/n: ')

    request_retry(url, is_main_url)


@retry(stop=(stop_after_attempt(1000) | stop_after_delay(50)))
def request_retry(url, is_main_url=False):
    global REQUEST_SESSION, REQUEST_HEADERS, REQUEST_SESSION_MAIN_URL_COUNT, REQUEST_SESSION_COUNT, REQUEST_ERROR_COUNT, REQUEST_ERROR_MAX_COUNT

    if not REQUEST_SESSION:
        REQUEST_SESSION = requests.Session()
    if REQUEST_SESSION_COUNT == 20:
        REQUEST_SESSION.cookies.clear()
        REQUEST_SESSION_COUNT = 0
        REQUEST_HEADERS = None
    if REQUEST_SESSION_MAIN_URL_COUNT == 15:
        REQUEST_SESSION = requests.Session()
        REQUEST_SESSION_MAIN_URL_COUNT = 0
        REQUEST_HEADERS = None
    if is_main_url:
        REQUEST_SESSION_MAIN_URL_COUNT = REQUEST_SESSION_MAIN_URL_COUNT + 1

    # 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'
    if not REQUEST_HEADERS:
        REQUEST_HEADERS = set_agent()
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': REQUEST_HEADERS,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }
    print('[+] ' + url)

    try:
        resp = REQUEST_SESSION.get(
            url, headers=headers, timeout=20, allow_redirects=True)
        if resp.status_code >= 500:
            print('[-] RETRY: code is 500')
            if REQUEST_ERROR_COUNT == REQUEST_ERROR_MAX_COUNT:
                # REQUEST_SESSION.cookies.clear()
                another_request(url, is_main_url)
            else:
                REQUEST_ERROR_COUNT = REQUEST_ERROR_COUNT + 1
                raise TryAgain
        # this is special
        # 404 in this site is actually a response
        elif resp.status_code == 404:
            REQUEST_SESSION_COUNT = REQUEST_SESSION_COUNT + 1
            return resp
        elif resp.status_code == 403:
            print('[-] RETRY: code is 403')
            if REQUEST_ERROR_COUNT == REQUEST_ERROR_MAX_COUNT:
                # REQUEST_SESSION.cookies.clear()
                another_request(url, is_main_url)
            else:
                REQUEST_ERROR_COUNT = REQUEST_ERROR_COUNT + 1
                raise TryAgain
        elif resp.status_code < 400:
            if 'Are you a real person?' in resp.text:
                print('[-] RETRY: bot check active')
                if REQUEST_ERROR_COUNT == REQUEST_ERROR_MAX_COUNT:
                    # REQUEST_SESSION.cookies.clear()
                    another_request(url, is_main_url)
                else:
                    REQUEST_ERROR_COUNT = REQUEST_ERROR_COUNT + 1
                    raise TryAgain
            else:
                REQUEST_ERROR_COUNT = 0
                REQUEST_SESSION_COUNT = REQUEST_SESSION_COUNT + 1
                return resp
        else:
            REQUEST_ERROR_COUNT = 0
            return Exception
    except Exception:
        raise TryAgain


class WineSearcher:
    global REQUEST_ERROR_COUNT

    def __init__(self, s=1, tr=1, btype='producer'):
        self.current_page = s
        if s > 1:
            self.start_count = ((s - 1) * 25) + 1
        else:
            self.start_count = 1
        self.start_tr = tr
        self.csv_fname = 'WINE-SEARCHER' + '_' + \
            datetime.fromtimestamp(time.time()).strftime(
                '%Y-%m-%d_%I-%M') + '.csv'
        self.main_url = 'https://www.wine-searcher.com/biz/producers/usa?s={}' if btype == 'producer' else 'https://www.wine-searcher.com/biz/stores/usa?s={}'
        # self.write_csv([[
        #     'Name', 'Address', 'City', 'State', 'Postal', 'Wines', 'Business Type', 'Phone', 'Website', 'WineSearch Page'
        # ]])

    def request(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        print('[+] Requesting source... {}'.format(url))
        try:
            resp = requests.get(url, headers=headers,
                                timeout=20, allow_redirects=True)
            return resp
        except Exception as e:
            print('[-] ERROR >> {}: {}'.format(url, str(e)))
            return False

    def get_data(self):
        pagination = True
        total_page = None
        current_page = self.current_page
        start_count = self.start_count
        request_count = 0

        while pagination:
            print('-----------------------------> PAGE: {}'.format(current_page))

            if current_page == total_page:
                pagination = False

            resp = request_retry(self.main_url.format(
                start_count), is_main_url=True if self.start_tr == 1 else False)
            if resp:
                soup = BeautifulSoup(resp.text, 'lxml')
                if not total_page:
                    total_page = int(soup.select('a.pager')
                                     [-2].get_text().strip())

                trs = soup.select('tr.wlrwdt')
                if self.start_tr > 1:
                    trs = trs[self.start_tr - 1:]
                for tr_i, tr in enumerate(trs):
                    address = None
                    city = None
                    state = None
                    postal = None

                    tds = tr.select('td')
                    a = tds[0].find('a')
                    name = a.get_text().strip()
                    profile = a.get('href').strip()
                    btype = tds[1].get_text().strip()
                    wines = tds[2].get_text().replace('Wines:', '').strip()
                    _addr = tds[3].get_text().strip()
                    if _addr.endswith(','):
                        _addr = _addr[:-1]

                    if 'No address given' in _addr:
                        pass
                    else:
                        try:
                            old_addr = _addr.strip()
                            _addr = [i.strip() for i in _addr.split(',')]
                            if len(_addr) == 1:
                                _tmp = old_addr.split(' ')
                                if len(_tmp[-2]) == 2:
                                    address = ', '.join(_tmp[0:-2])
                                    state = _tmp[-2]
                                    postal = _tmp[-1]
                                    city = None
                            else:
                                address = ', '.join(_addr[0:-2])
                                city = _addr[-2]
                                if len(_addr[-1].split(' ')) == 3:
                                    city, state, postal = tuple(
                                        [i.strip() for i in _addr[-1].split(' ')])
                                elif len(_addr[-1].split(' ')) == 1:
                                    city = None
                                    state = _addr[-2]
                                    postal = _addr[-1]
                                else:
                                    try:
                                        state, postal = tuple(
                                            [i.strip() for i in _addr[-1].split(' ')])
                                    except Exception:
                                        _tmp = _addr[-1].split(' ')
                                        city = ' '.join(_tmp[:-2])
                                        state = _tmp[-2]
                                        postal = _tmp[-1]
                        except Exception:
                            pass

                    phone = None
                    website = None
                    resp = request_retry(profile)
                    try:
                        soup = BeautifulSoup(resp.text, 'lxml')
                    except Exception:
                        soup = None
                    try:
                        phone = soup.find(
                            'span', {'itemprop': 'telephone'}).get_text().strip()
                    except Exception:
                        pass
                    try:
                        website = soup.find('span', text='Website').find_parent('a').get(
                            'onmouseover').replace('this.href=', '').replace("'", '').strip()
                    except Exception:
                        try:
                            website = soup.find(
                                'meta', {'itemprop': 'url'}).get('content')
                        except Exception:
                            pass

                    data = [[
                        name, address, city, state, postal, wines, btype, phone, website, profile
                    ]]
                    self.write_csv(data)
                    print('[+] Done >> ' + name)

                    request_count = request_count + 1

                    with open('page-tr.txt', 'w') as f:
                        f.write('{} - {}'.format(current_page,
                                                 tr_i + self.start_tr))

                self.start_tr = 1
                current_page = current_page + 1
                start_count = start_count + 25

    def write_csv(self, data):
        try:
            with open(self.csv_fname, 'a') as f:
                writer = csv.writer(f)
                for d in data:
                    writer.writerow([e for e in d])
                    f.flush()
        except Exception as e:
            print('[-] CSV ERROR: {}'.format(e))


def notify():
    note = notify2.Notification('ALERT!', 'Change VPN or check `Bot Check`!')
    note.set_category('network')
    note.set_timeout(50000)
    note.show()


if __name__ == '__main__':
    notify2.init('WINE SCRAPER')

    s = 1
    tr = 1
    btype = sys.argv[1]
    if len(sys.argv) == 3:
        s = int(sys.argv[2])
    elif len(sys.argv) == 4:
        s = int(sys.argv[2])
        tr = int(sys.argv[3])
    ws = WineSearcher(s, tr, btype)
    ws.get_data()
