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
NAME = 'DiscoverCloud'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

MAIN_URL = 'https://www.discovercloud.com'


class DiscoverCloud:
    def get_categories(self):
        cats = []
        resp = request(MAIN_URL)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            cats = sorted(list(set(['https://www.discovercloud.com' + \
                                    a.get('href') for a in soup.find_all('a', {'href': \
                                    re.compile(r'/categories/')}) if a.get_text().strip()])))
        return cats

    def get_profiles(self, category):
        profiles = []

        total_page_scraped = False
        total_page = 1
        current_page = 1
        while total_page != 0:
            logger.info('Getting profiles - {}'.format(category + f'?pn={current_page}&tpo=true'))
            resp = request(category + f'?pn={current_page}&tpo=true')
            if resp:
                soup = BeautifulSoup(resp.text, 'lxml')

                if not total_page_scraped:
                    _p = soup.find('div', id='ckt-paging-box').find('span').get_text().strip().split()
                    try:
                        total_page = int(_p[-1])
                        total_page_scraped = True
                    except Exception:
                        pass

                profiles.extend(['https://www.discovercloud.com' + a.get('href') for a in \
                                 soup.find('div', class_='ckt-search-boxes-wrapper').find_all('a', \
                                 {'href': re.compile(r'/products/')}) if 'reviews' not in a.get('href')])
                total_page = total_page - 1
                current_page = current_page + 1
        profiles = sorted(list(set(profiles)))
        return profiles

    def get_data(self, url):
        logger.info(f'Getting source - {url}')
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            vendor = self.get_vendor(soup)
            website = self.get_website(soup)
            desc = self.get_description(soup)
            features = self.get_features(soup)
            pricing = self.get_pricing(soup)
            rating = self.get_rating(soup)
            reviews = self.get_reviews(soup)
            category = self.get_category(soup)
            profile = url

            data = [[
                name,
                vendor,
                website,
                desc,
                features,
                pricing,
                rating,
                reviews,
                category,
                profile
            ]]
            write_data(data, name)

    def get_name(self, soup):
        try:
            return soup.find('h1').get_text().strip()
        except Exception:
            return None

    def get_vendor(self, soup):
        try:
            return soup.find('h2', class_='ckt-inline').find('a').get_text().strip()
        except Exception:
            return None

    def get_website(self, soup):
        try:
            return get_fld(soup.find('a', class_='ckt-external-link-btn').get('href').strip())
        except Exception:
            return None

    def get_category(self, soup):
        try:
            return soup.find('div', class_='ckt-category').get_text().strip()
        except Exception:
            return None

    def get_description(self, soup):
        try:
            return soup.find('div', class_='ckt-what-about-wrapper').find('p').get_text().strip()
        except Exception:
            return None

    def get_features(self, soup):
        try:
            return soup.find('h3', text=re.compile(r'Key Features')).find_next('p').get_text().strip()
        except Exception:
            return None

    def get_rating(self, soup):
        try:
            return re.findall(r'\d.+', soup.find('span', class_='ckt-avarage').get_text().strip())[0]
        except Exception:
            return None

    def get_reviews(self, soup):
        try:
            return soup.find('span', class_='ckt-votes').get_text().strip()
        except Exception:
            return None

    def get_pricing(self, soup):
        try:
            p = soup.find('h3', text=re.compile(r'Pricing')).find_next('p')
            for br in p.find_all('br'):
                br.replaceWith('\n')
            return p.get_text().strip()
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
        'Company',
        'Website',
        'Description',
        'Features',
        'Pricing',
        'Rating',
        'Reviews',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = DiscoverCloud()
    cats = mod.get_categories()
    for cat in cats:
        profiles = mod.get_profiles(cat)
        for profile in profiles:
            mod.get_data(profile)


def get_data():
    main()
