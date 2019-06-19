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
from utils import setup_logger, request, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'CardLife'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

MAIN_URL = 'https://www.cardlifeapp.com/saas-directory'


class Cardlife:
    def get_categories(self):
        logger.info('Getting categories.')
        resp = request(MAIN_URL)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            return [a.get('href').strip() for a in soup.select('.saas-category-list-body a')]
        return []

    def get_profiles(self, cats):
        profiles = []
        for cat in cats:
            cat_name = cat.rpartition('/')[-1]
            logger.info(f'Getting profiles for {cat_name}')

            resp = request(cat)
            if resp:
                soup = BeautifulSoup(resp.text, 'lxml')
                urls = [a.get('href').strip() for a in soup.select('a.saas-category-item-name')]
                profiles.append({
                    cat_name: urls
                })
        return profiles

    def get_profile_data(self, cat, url):
        logger.info(f'{cat} - {url}')
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            try:
                name = soup.find('h1', class_='saas-item-name').get_text().strip()
            except:
                return False
            try:
                website = get_fld(soup.find('a', class_='saas-visit-website-btn').get('href').strip())
            except:
                website = ''
            try:
                desc = soup.find('h1', class_='saas-item-name').find_next('div').get_text().strip()
            except:
                desc = ''

            data = [[name, website, desc, cat, url]]
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
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = Cardlife()
    cats = mod.get_categories()
    profiles = mod.get_profiles(cats)
    for profile in profiles:
        for category, urls in profile.items():
            for url in urls:
                mod.get_profile_data(category, url)


def get_data():
    main()
