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
NAME = 'SaasHub'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

CATEGORIES_URL = 'https://www.saashub.com/categories'


class SaasHub:
    def get_categories(self):
        categories = []
        resp = request(CATEGORIES_URL)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            categories = ['https://www.saashub.com' + a.get('href') for a in soup.select('ul.categories-list li a')]
        return categories

    def get_profiles(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            return ['https://www.saashub.com' + a.get('href') for a in soup.select('h3 a')]
        return []

    def get_data(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            if not name:
                return False
            desc = self.get_desc(soup)
            website = self.get_website(soup)
            tw = self.get_twitter(soup)
            cats = self.get_cats(soup)

            data = [[
                name, website, desc, tw, cats, url
            ]]
            write_data(data, name)

    def get_name(self, soup):
        try:
            return soup.find('div', class_='title').get_text().strip()
        except Exception:
            return None

    def get_website(self, soup):
        try:
            return get_fld(soup.find('a', text=re.compile('^Visit.+Website$')).get('href').strip())
        except Exception:
            return None

    def get_desc(self, soup):
        try:
            return soup.find('h3', class_='subtitle').get_text().replace(';', ',').strip()
        except Exception:
            return None

    def get_twitter(self, soup):
        try:
            return soup.find('a', {'href': re.compile('^https://twitter.com/'), \
                        'class': 'button is-light is-outlined'}).get('href').strip()
        except Exception:
            return None

    def get_cats(self, soup):
        try:
            return ', '.join([a.get_text().strip() for a in soup.find('div', class_='service-categories').find_all('a')])
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
        'Twitter',
        'Categories',
        'Profile'
    ]])


def main():
    csv_header()
    mod = SaasHub()
    cats = mod.get_categories()
    for cat in cats:
        profiles = mod.get_profiles(cat)
        for p in profiles:
            mod.get_data(p)


def get_data():
    main()
