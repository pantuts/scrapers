#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import json
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
NAME = 'Stripe'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

MAIN_URL = 'https://stripe.com'
BROWSE_URL = 'https://stripe.com/works-with'


class Stripe:
    def get_categories(self):
        resp = request(BROWSE_URL)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            return ['https://stripe.com' + a.get('href').strip() for a \
                in soup.find_all('a', attrs={'href': re.compile(r'/works-with/categories/')})]
        return None

    def get_json(self, soup):
        try:
            s = soup.select('#js-page-context')[0]
            return json.loads(re.findall(r'\{.+', str(s))[0])
        except Exception:
            return False

    def get_data(self, cat_url):
        resp = request(cat_url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            json_data = self.get_json(soup)
            if json_data:
                for item in json_data.get('main_category').get('integrations'):
                    name = item.get('company').strip()
                    cat = item.get('category_name').strip()
                    desc = item.get('description_html').strip().replace(';', ',')
                    rating = item.get('rating')
                    profile = MAIN_URL + item.get('permalink')
                    site = item.get('company_url')
                    if site:
                        if not site.startswith('http'):
                            site = 'http://' + site
                        site = get_fld(site)
                    data = [[
                        name,
                        site,
                        desc,
                        rating,
                        cat,
                        profile
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
        'Website',
        'Description',
        'Rating',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = Stripe()
    cats = mod.get_categories()
    for cat in cats:
        mod.get_data(cat)


def get_data():
    main()
