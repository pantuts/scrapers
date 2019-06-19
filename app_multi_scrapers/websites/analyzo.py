#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import config
import os
import re
import requests
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_fld
from utils import setup_logger, request, get_sitemap_locs, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'Analyzo'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

SITEMAP_URL = 'http://www.analyzo.com/sitemap.xml'


class Analyzo:
    def get_profiles(self):
        logger.info(SITEMAP_URL)
        final_locs = []
        _locs = get_sitemap_locs(SITEMAP_URL)
        for _loc in _locs:
            if _loc.startswith('https://www.analyzo.com/product-details/'):
                final_locs.append(_loc)
        final_locs = list(set(final_locs))
        return final_locs

    def get_data(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            try:
                h1 = soup.find('h1')
                h1.find('span', class_='claim').replaceWith('')
                h1 = h1.get_text().strip()
                name = h1.split(' by ')[0].strip()
                by = h1.split(' by ')[1].strip()
            except Exception:
                return False

            try:
                cat = soup.find('ol', class_='breadcrumb').find_all('li')[-2].get_text().strip()
            except Exception:
                cat = None

            try:
                u = soup.find('a', text=re.compile(r'Visit Website')).get('href').strip()
                if 'bit.ly' in u:
                    website = requests.head(u).headers.get('Location')
                else:
                    website = u
                website = get_fld(website)
            except Exception:
                website = None

            try:
                desc = soup.find('div', id='getwiddes').find('p').get_text().strip()
            except Exception:
                desc = None

            try:
                vote = soup.find('button', class_='votup-btn').find('span', id=re.compile(r'count_[0-9]|count')).get_text().strip()
            except Exception:
                vote = 0

            data = [[name, by, website, desc, vote, cat, url]]
            write_data(data, name)


def write_data(data, name=None):
    done = csv_utils.write_csv(CSV_FNAME, data, NOW)
    if name:
        if done:
            logger.info(f'[CSV] Done >> {name}')


def main():
    write_data([['Name', 'Company', 'Website', 'Description', 'Upvotes', 'Category', 'Profile']])
    mod = Analyzo()
    profiles = mod.get_profiles()
    for url in profiles:
        mod.get_data(url)


def get_data():
    main()
