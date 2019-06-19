#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import notify2
import os
import random
import re
import sys
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_fld
from utils import setup_logger, request, get_sitemap_locs, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'TrustRadius'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

SITEMAP_URL = 'https://www.trustradius.com/sitemap_productreview.xml'
REQUEST_ERROR = 0


def notify():
    try:
        note = notify2.Notification('ALERT!', 'Change VPN!')
        note.set_category('network')
        note.set_timeout(50000)
        note.show()
    except Exception:
        logger.error('Alert! Change VPN!')


def request_restart(url):
    global REQUEST_ERROR

    REQUEST_ERROR = REQUEST_ERROR + 1
    if REQUEST_ERROR == 5:
        return False

    notify()
    vpn_restarted = 'n'
    while vpn_restarted != 'y':
        vpn_restarted = input('Started? y/n: ')

    resp = request(url)
    if not resp:
        request_restart(url)
    else:
        REQUEST_ERROR = 0
        if 'rate limit exceeded' in resp.text.lower():
            request_restart(url)
        else:
            return resp


def sleep():
    for i in range(random.randint(40, 60)):
        sys.stdout.write('Resuming in {}\r\n'.format(i))
        sys.stdout.flush()
        time.sleep(1)


class TrustRadius:
    def __init__(self):
        self.err_count = 0

    def get_profiles(self):
        final_locs = []
        _locs = get_sitemap_locs(SITEMAP_URL)
        for _loc in _locs:
            if _loc.startswith('https://www.trustradius.com/products/') and _loc.endswith('/reviews'):
                final_locs.append(_loc)
        final_locs = list(set(final_locs))
        return final_locs

    def get_data(self, url):
        resp = request(url)
        if resp:
            if 'rate limit exceeded' in resp.text.lower():
                if self.err_count == 5:
                    return False
                self.err_count = self.err_count + 1
                sleep()
                self.get_data(url)
            else:
                soup = BeautifulSoup(resp.text, 'lxml')
                name = self.get_name(soup)
                if not name:
                    logger.warning('Unable to get resp.text!')
                    return False
                website = self.get_website(soup)
                desc = self.get_description(soup)
                reviews = self.get_reviews(soup)
                rating = self.get_rating(soup)
                categories = self.get_categories(soup)
                data = [[
                    name,
                    website,
                    desc,
                    rating,
                    reviews,
                    categories,
                    url
                ]]
                write_data(data, name)
                self.err_count = 0
        else:
            if self.err_count == 5:
                return False
            self.err_count = self.err_count + 1
            sleep()
            self.get_data(url)

    def get_data2(self, url):
        soup = None
        resp = request(url)
        if resp:
            if 'rate limit exceeded' in resp.text.lower():
                resp = request_restart(url)
                if resp:
                    soup = BeautifulSoup(resp.text, 'lxml')
            else:
                soup = BeautifulSoup(resp.text, 'lxml')
        else:
            resp = request_restart(url)
            if resp:
                soup = BeautifulSoup(resp.text, 'lxml')

        name = self.get_name(soup)
        if not name:
            logger.warning('Unable to get resp.text!')
            return False
        website = self.get_website(soup)
        desc = self.get_description(soup)
        reviews = self.get_reviews(soup)
        rating = self.get_rating(soup)
        categories = self.get_categories(soup)
        data = [[
            name,
            website,
            desc,
            rating,
            reviews,
            categories,
            url
        ]]
        write_data(data, name)

    def get_name(self, soup):
        try:
            return soup.find('h1').find('span', {'itemprop': 'name'}).get_text().strip().replace(';', ',')
        except Exception:
            return None

    def get_website(self, soup):
        try:
            s = soup.find('a', class_='vendor-backlink').get('href')
            if not s.startswith('http'):
                s = 'http://' + s
            return get_fld(s)
        except Exception:
            return None

    def get_description(self, soup):
        try:
            return soup.find('div', class_='description').get_text().strip().replace(';', ',')
        except Exception:
            return None

    def get_rating(self, soup):
        try:
            return soup.find('span', attrs={'itemprop': 'ratingValue'}).get_text().strip()
        except Exception:
            return None

    def get_reviews(self, soup):
        try:
            s = soup.find('a', text=re.compile(r'Ratings and Reviews')).get_text().strip()
            return re.findall('[0-9]{1,8}', s)[0]
        except Exception:
            return None

    def get_categories(self, soup):
        try:
            for div in soup.find_all('div', class_='description'):
                if div.get_text().strip().startswith('Categories:'):
                    cats = ', '.join([a.get_text() for a in div.find_all('a')])
                    return cats
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
        'Categories',
        'Profile'
    ]])


def main():
    csv_header()
    mod = TrustRadius()
    profiles = mod.get_profiles()
    for profile in profiles:
        mod.get_data(profile)


def get_data():
    main()
