#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import config
import os
import re
import sys
import time

import gevent
import gevent.monkey
if 'threading' in sys.modules:
    del sys.modules['threading']

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_fld
from utils import setup_logger, request, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'ProgrammableWeb'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

MAIN_URL = 'https://www.programmableweb.com'
BROWSE_URL = 'https://www.programmableweb.com/category/all/apis?page={}'


class ProgrammableWeb:
    def get_profiles(self):
        page = 0
        pagination = True
        while pagination:
            resp = request(BROWSE_URL.format(page))
            if resp:
                soup = BeautifulSoup(resp.text, 'lxml')
                if 'Sorry, your search did not give any results' in str(soup):
                    pagination = False

                profiles = [MAIN_URL + a.get('href') for a in \
                        soup.select('.view-search-apis .views-field-title a')]

                threads = []
                for i in range(len(profiles)):
                    threads.append(gevent.spawn(self.get_data, profiles[i]))
                    if (i + 1) % config.THREAD_WORKERS == 0:
                        gevent.joinall(threads)
                    else:
                        continue
                gevent.joinall(threads)

                # for profile in profiles:
                #     self.get_data(profile)
            page = page + 1

    def get_data(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            try:
                name = soup.find('h1').get_text().strip().replace(' API', '')
            except Exception:
                return False

            try:
                provider = soup.find('label', text=re.compile('API Provider')).find_next('span').find_next('a').get_text().strip()
            except Exception:
                provider = None

            try:
                desc = soup.find('div', class_='api_description').get_text().strip().replace(';', '')
            except Exception:
                desc = None

            try:
                _w = soup.find('label', text=re.compile('Home Page')).find_next('span').find_next('a').get('href').strip()
                website = get_fld(_w)
            except Exception:
                website = None

            try:
                auth_model = soup.find('label', text=re.compile('Authentication Model')).find_next('span').get_text().strip()
            except Exception:
                auth_model = None

            try:
                scope = soup.find('label', text=re.compile('Scope')).find_next('span').get_text().strip()
            except Exception:
                scope = None

            try:
                device_specific = soup.find('label', text=re.compile('Device Specific')).find_next('span').get_text().strip()
            except Exception:
                device_specific = None

            try:
                formats = soup.find('label', text=re.compile('Supported Request Formats')).find_next('span').get_text().strip()
            except Exception:
                formats = None

            try:
                category = soup.find('label', text=re.compile('Primary Category')).find_next('span').find_next('a').get_text().strip()
            except Exception:
                category = None

            data = [[
                name,
                provider,
                website,
                desc,
                auth_model,
                scope,
                device_specific,
                formats,
                category,
                url
            ]]
            write_data(data, name)


def write_data(data, name=None):
    done = csv_utils.write_csv(CSV_FNAME, data, NOW)
    if name:
        if done:
            logger.info(f'[CSV] Done >> {name}')


def csv_header():
    write_data([[
        'Name',
        'Company',
        'Website',
        'Description',
        'Auth Model',
        'Scope',
        'Device Specific',
        'Formats',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = ProgrammableWeb()
    mod.get_profiles()


def get_data():
    main()
