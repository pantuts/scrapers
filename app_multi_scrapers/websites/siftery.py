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
from utils import setup_logger, request, get_sitemap_locs, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'Siftery'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

CATEGORIES_URL = 'https://siftery.com/categories'
CATEGORIES_PRODUCTS_URL = 'https://siftery.com/inapi/categories/{}/{}/products'
PRODUCTS_API_URL = 'https://siftery.com/inapi/product-json/{}'


class Siftery:
    def get_categories(self):
        categories = []
        resp = request(CATEGORIES_URL)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            js_cats = re.findall(r'window.siftery.CATEGORIES.push\(({.+?})\)', str(soup))
            for cats in js_cats:
                parent_cat = json.loads(cats)
                final_category = {}
                for handle_cats in parent_cat.get('categories'):
                    fcat = handle_cats.get('handle')
                    final_category[fcat] = []
                    for cat in handle_cats.get('categories'):
                        final_category[fcat].append(cat.get('handle'))
                categories.append(final_category)
        return categories

    def get_products(self, cat_dict):
        fcat = list(cat_dict.keys())[0]
        for cat_name in cat_dict.get(fcat):
            cat_prod_url = CATEGORIES_PRODUCTS_URL.format(fcat, cat_name)

            resp = request(cat_prod_url)
            if resp:
                try:
                    jsn_cat_prod = resp.json()
                except Exception:
                    jsn_cat_prod = {}
                if jsn_cat_prod:
                    products = jsn_cat_prod.get('content').get('products')
                    for prod in products:
                        product = {
                            'name': None,
                            'handle': None,
                            'desc': None,
                            'customers': 0,
                            'score': 0,
                            'reviews_up': 0,
                            'reviews_down': 0,
                            'primary_category': None,
                            'other_categories': None,
                            'website': None,
                            'profile': None
                        }
                        product['name'] = prod.get('name')
                        product['handle'] = prod.get('handle')
                        desc = prod.get('description')
                        if desc:
                            desc = desc.replace(';', ',')
                        product['desc'] = desc
                        meta = prod.get('metadata')
                        product['customers'] = meta.get('num_customers')
                        nps = meta.get('nps')
                        product['score'] = round(nps.get('nps_score'))
                        product['reviews_up'] = nps.get('detractor_count')
                        product['reviews_down'] = nps.get('promoter_count')
                        product['profile'] = 'https://siftery.com/{}'.format(prod.get('handle'))

                        resp = request(PRODUCTS_API_URL.format((product['handle'])))
                        if resp:
                            try:
                                jsn_prod = resp.json()
                            except Exception:
                                jsn_prod = {}

                            if jsn_prod:
                                content = jsn_prod.get('content')
                                site = content.get('product').get('website_url')
                                if site:
                                    if not site.startswith('http'):
                                        site = 'http://' + site
                                    product['website'] = get_fld(site)
                                product['primary_category'] = content.get('primary_category').get('name')
                                product['other_categories'] = ', '.join([n.get('name') for n in content.get('other_categories')])

                        data = [[
                            product.get('name'),
                            product.get('website'),
                            product.get('desc'),
                            product.get('customers'),
                            product.get('reviews_up'),
                            product.get('reviews_down'),
                            product.get('score'),
                            product.get('primary_category'),
                            product.get('other_categories'),
                            product.get('profile')
                        ]]
                        write_data(data, product.get('name'))


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
        'Customers',
        'Reviews Up',
        'Reviews Down',
        'Score',
        'Primary Category',
        'Other Categories',
        'Profile'
    ]])


def main():
    csv_header()
    mod = Siftery()
    cats = mod.get_categories()
    for cat in cats:
        mod.get_products(cat)


def get_data():
    main()
