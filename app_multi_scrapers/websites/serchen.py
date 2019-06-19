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
from utils import setup_logger, request, get_sitemap_locs, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'Serchen'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

SITEMAP_URL = 'http://www.serchen.com/sitemap.xml'


class Serchen:
    def get_profiles(self):
        final_locs = []
        _locs = get_sitemap_locs(SITEMAP_URL)
        for _loc in _locs:
            if _loc.startswith('https://www.serchen.com/company/') and not _loc.endswith('similar-companies/'):
                final_locs.append(_loc)
        final_locs = list(set(final_locs))
        return final_locs

    def get_data(self, url):
        resp = request(url, use_headers=False)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            website = self.get_website(soup)
            rating = self.get_rating(soup)
            reviews = self.get_reviews(soup)
            category = self.get_category(soup)
            profile = url

            data = [[name, website, rating, reviews, category, profile]]
            write_data(data, name)

    def get_name(self, soup):
        try:
            return soup.find('h1', class_='page-title').get_text().strip()
        except Exception:
            return None

    def get_website(self, soup):
        try:
            s = soup.find('li', attrs={'style': re.compile('link_grey.png')}).get_text().strip()
            if not s.startswith('http'):
                s = 'http://' + s
            return get_fld(s)
        except Exception:
            return None

    def get_rating(self, soup):
        try:
            r = soup.find('h3', class_='average-rating').get_text().strip()
            if r == '0.0':
                r = 0
            return r
        except: return '0'

    def get_reviews(self, soup):
        try:
            r = soup.find('div', class_='rating-overview').find('span', class_='count').get_text().strip()
            return ''.join(re.findall('[0-9]', r))
        except Exception:
            return None

    def get_category(self, soup):
        try:
            return soup.find('a', attrs={'href': re.compile('/category/')}).get_text().strip()
        except Exception:
            return None


def write_data(data, name=None):
    done = csv_utils.write_csv(CSV_FNAME, data, NOW)
    if name:
        if done:
            logger.info(f'[CSV] Done >> {name}')


def csv_header():
    write_data([[
        'Name',
        'Website',
        'Rating',
        'Reviews',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = Serchen()
    profiles = mod.get_profiles()
    for profile in profiles:
        mod.get_data(profile)


def get_data():
    main()
