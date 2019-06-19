#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import os
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_fld
from utils import setup_logger, request, get_sitemap_locs, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'SaasGenius'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

SITEMAP_URL = 'http://www.saasgenius.com/sitemap.xml'


class SaasGenius:
    def get_profiles(self):
        final_locs = []
        _locs = get_sitemap_locs(SITEMAP_URL)
        for _loc in _locs:
            if _loc.startswith('http://www.saasgenius.com/program/'):
                if not _loc.endswith('/alternatives') or not _loc.endswith('/comparisons'):
                    final_locs.append(_loc)
        final_locs = list(set(final_locs))
        return final_locs

    def get_data(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            if not name:
                return False
            website = self.get_website(soup)
            desc = self.get_description(soup)
            features = self.get_features(soup)
            specs = self.get_specs(soup)
            pricing = self.get_pricing(soup)
            rating = self.get_rating(soup)
            reviews = self.get_reviews(soup)
            category = self.get_category(soup)
            profile = url

            data = [[
                name,
                website,
                desc,
                features,
                specs,
                pricing,
                rating,
                reviews,
                category,
                profile
            ]]
            write_data(data, name)

    def get_name(self, soup):
        try:
            return soup.find('div', class_='top-title').get_text().strip()
        except Exception:
            return None

    def get_website(self, soup):
        try:
            return get_fld(soup.find('div', class_='link-top').find('a').get('href').strip())
        except Exception:
            return None

    def get_category(self, soup):
        try:
            return soup.find('div', class_='top-subtitle').get_text().strip()
        except Exception:
            return None

    def get_description(self, soup):
        try:
            return soup.find('h2', class_='title-program').find_next('p').get_text().strip()
        except Exception:
            return None

    def get_features(self, soup):
        try:
            return ', '.join([li.get_text() for li in soup.select('div.key-features li')])
        except Exception:
            return None

    def get_specs(self, soup):
        try:
            return '\n'.join([div.get_text().strip().replace('\n\n\n', ': ') \
                for div in soup.select('div.specification div.row')])
        except Exception:
            return None

    def get_rating(self, soup):
        try:
            return soup.find('span', class_='average-rating').find('span').get_text().strip()
        except Exception:
            return None

    def get_reviews(self, soup):
        try:
            return soup.find('span', class_='total-votes').find('span').get_text().strip()
        except Exception:
            return None

    def get_pricing(self, soup):
        try:
            return soup.find('div', class_='pricing').get_text().strip().replace('\n\n\n', '\n').replace('\n\n', '\n')
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
        'Features',
        'Specs',
        'Pricing',
        'Rating',
        'Reviews',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = SaasGenius()
    profiles = mod.get_profiles()
    for profile in profiles:
        mod.get_data(profile)


def get_data():
    main()
