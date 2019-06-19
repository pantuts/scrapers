#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import os
import requests
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_fld
from utils import setup_logger, request, get_sitemap_locs, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'SoftwareAdvice'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

SITEMAP_URL = 'http://www.softwareadvice.com/sitemap.xml'


class SoftwareAdvice:
    def get_data(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            site = self.get_website(soup)
            desc = self.get_description(soup)
            reviews = self.get_reviews(soup)
            rating = self.get_rating(soup)
            category = self.get_category(soup)
            data = [[name, site, desc, rating, reviews, category, url]]
            write_data(data, name)

    def get_profiles(self):
        final_locs = []
        _locs = get_sitemap_locs(SITEMAP_URL)
        for _loc in _locs:
            if '-profile' in _loc and _loc.endswith('-profile/'):
                final_locs.append(_loc)
        final_locs = list(set(final_locs))
        return final_locs

    def get_name(self, soup):
        try:
            return soup.find('h1').get_text().strip()
        except Exception:
            return None

    def get_website(self, soup):
        try:
            s = soup.find('a', class_='visit-website-button').get('href')
            if not s.startswith('http'):
                s = 'http://' + s
            if 'external_click' in s:
                resp = requests.head(s)
                s = resp.headers.get('Location')
            return get_fld(s)
        except Exception:
            return None

    def get_description(self, soup):
        try:
            return soup.find('div', id='ellipsys-executed').get_text().replace(';', '').strip()
        except Exception:
            return None

    def get_category(self, soup):
        try:
            return soup.find('ul', class_='breadcrumbs').find_all('li')[-2].get_text().strip()
        except Exception:
            return None

    def get_rating(self, soup):
        try:
            return soup.find('span', id='rating-value').get_text().strip()
        except Exception:
            return None

    def get_reviews(self, soup):
        try:
            return soup.find('span', id='review-count').get_text().strip()
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
        'Description',
        'Rating',
        'Reviews',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = SoftwareAdvice()
    profiles = mod.get_profiles()
    for profile in profiles:
        mod.get_data(profile)


def get_data():
    main()
