#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import os
import re
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_fld
from utils import setup_logger, request, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'Crozdesk'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

MAIN_URL = 'https://crozdesk.com/browse'


class CrozDesk:
    def __init__(self):
        self.profiles = []

    def get_categories(self):
        print('[+] Getting categories...')
        resp = request(MAIN_URL)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            return ['https://crozdesk.com' + a.get('href').strip() for a \
                in soup.select('div#categories div.cus_categories-block ul li a')]
        return []

    def get_profiles(self, cat_url):
        logger.info(f'Getting profiles - {cat_url}')
        resp = request(cat_url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            return ['https://crozdesk.com' + a.get('href').strip() for a \
                in soup.select('a.cus_listingbox-title')]
        return []

    def get_data(self, url):
        logger.info(f'Getting source - {url}')
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            try:
                name = soup.find('h1').get_text().strip()
            except Exception:
                return False
            try:
                _site = soup.select('table.crozscore-trend .btn-quicklink')[0].get_text().strip()
                if not _site.startswith('http://'):
                    _site = 'http://' + _site
                website = get_fld(_site)
            except Exception:
                website = None

            try:
                desc = soup.find('div', id='provider_description').get_text().strip()
            except Exception:
                desc = None

            try:
                rating = soup.find('span', attrs={'itemprop': 'ratingValue'}).get_text().strip()
            except Exception:
                rating = None

            try:
                rating_c = soup.find('span', attrs={'itemprop': 'ratingCount'}).get_text().strip()
            except Exception:
                rating_c = None

            try:
                cat = soup.find('span', attrs={'itemprop': 'applicationCategory'}).get_text().strip()
            except Exception:
                cat = None

            try:
                pricing = soup.find('span', text=re.compile(r'Pricing')).find_next('span').get_text().strip()
            except Exception:
                pricing = None

            data = [[name, website, desc, rating, rating_c, pricing, cat, url]]
            write_data(data, name)


def write_data(data, name=None):
    done = csv_utils.write_csv(CSV_FNAME, data, NOW)
    if name:
        if done:
            logger.info(f'[CSV] Done >> {name}')


def csv_header():
    write_data([[
        'Name',
        'Website',
        'Description',
        'Rating',
        'Reviews',
        'Pricing',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = CrozDesk()
    cats = mod.get_categories()
    for cat in cats:
        profiles = mod.get_profiles(cat)
        for profile in profiles:
            mod.get_data(profile)


def get_data():
    main()
