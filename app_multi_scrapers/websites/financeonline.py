#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import notify2
import os
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_fld
from utils import setup_logger, request, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'FinanceOnline'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

MAIN_URL = 'https://reviews.financesonline.com/page/{}/'
REQUEST_ERROR = 0


def request_restart(url):
    global REQUEST_ERROR

    REQUEST_ERROR = REQUEST_ERROR + 1
    if REQUEST_ERROR == 3:
        notify()
        vpn_restarted = 'n'
        while vpn_restarted != 'y':
            vpn_restarted = input('Started? y/n: ')
    elif REQUEST_ERROR == 5:
        return False

    resp = request(url)
    if not resp:
        request_restart(url)
    else:
        REQUEST_ERROR = 0
        return resp


def profile_data(resp):
    desc = None
    features = None
    website = None
    reviews = None

    if resp:
        soup = BeautifulSoup(resp.text, 'lxml')
        _desc = soup.find('div', class_='product-description')
        if _desc:
            desc = _desc.get_text().strip()
        _feat = soup.select('ul.tick-list li')
        if _feat:
            features = ', '.join([li.get_text() for li in _feat])
        _site = soup.find('div', class_='review-app-domain')
        if _site:
            website = _site.get_text().strip()
            if not website.startswith('http'):
                website = 'http://' + website
            try:
                website = get_fld(website)
            except Exception:
                website = None
        try:
            reviews = float(soup.find('span', class_='review-count').get_text().replace('user reviews', '').strip())
        except Exception:
            pass
    return desc, features, website, reviews


class FinanceOnline:
    def get_products(self):
        page = 1
        total_page = 1
        total_page_scraped = False

        while total_page != 0:
            resp = request(MAIN_URL.format(page))
            if resp:
                soup = BeautifulSoup(resp.text, 'lxml')
                _prods = soup.select('div.all_products_table div.row')

                if not total_page_scraped:
                    total_page = int(soup.find('span', class_='pages').get_text().strip().split()[-1])
                    total_page_scraped = True

                for div in _prods[1:]:
                    div_name = div.find('div', class_='product_name')
                    name = div_name.get_text().strip()
                    profile = 'https://reviews.financesonline.com' + div_name.find('a').get('href')
                    category = div.find('div', class_='category_name').get_text().strip()
                    score = div.find('div', class_='smart_score_name').get_text().strip()
                    price = div.find('div', class_='price_name').get_text().strip()
                    user_sat = div.find('div', class_='user_sat_name').get_text().strip()
                    support = div.find('div', class_='support_name').get_text().strip()

                    resp = request(profile)
                    if resp:
                        desc, features, website, reviews = profile_data(resp)
                    else:
                        resp = request_restart(profile)
                        desc, features, website, reviews = profile_data(resp)

                    data = [[
                        name,
                        website,
                        desc,
                        features,
                        price,
                        score,
                        user_sat,
                        reviews,
                        support,
                        category,
                        profile
                    ]]
                    write_data(data, name)

            page = page + 1
            total_page = total_page - 1


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
        'Price',
        'Score',
        'User Satisfaction',
        'Reviews',
        'Support',
        'Category',
        'Profile'
    ]])


def notify():
    try:
        note = notify2.Notification('ALERT!', 'Change VPN!')
        note.set_category('network')
        note.set_timeout(50000)
        note.show()
    except Exception:
        logger.debug('Alert! Change VPN!')


def main():
    try:
        notify2.init('Finance Online Scraper')
    except Exception:
        logger.info('Notify Init: Finance Online Scraper')

    csv_header()
    mod = FinanceOnline()
    mod.get_products()


def get_data():
    main()
