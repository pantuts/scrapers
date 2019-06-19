#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import config
import os
import re
import sys
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_fld
from utils import setup_logger, request, CSVUtils

import gevent
import gevent.monkey
if 'threading' in sys.modules:
    del sys.modules['threading']
# gevent.monkey.patch_all()

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'Capterra'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

CATEGORIES_URL = 'http://www.capterra.com/categories'


class Capterra:
    def get_categories(self):
        try:
            cats= []
            resp = request(CATEGORIES_URL)
            soup = BeautifulSoup(resp.text, 'lxml')
            links = soup.select('.browse-group-list a')
            for a in links:
                cats.append((
                    a.get_text().strip(),
                    'https://www.capterra.com/' + a.get('href').strip()
                ))
            return cats
        except Exception as e:
            logger.error(str(e))
            return []

    def get_profiles(self, cat_tuple):
        try:
            cat = cat_tuple[0]
            profiles = []
            resp = request(cat_tuple[1])
            soup = BeautifulSoup(resp.text, 'lxml')
            links = soup.select('p.listing-description .spotlight-link')
            for i, a in enumerate(links):
                profiles.append((
                    cat,
                    'https://www.capterra.com' + a.get('href').strip(),
                    i + 1
                ))
            # category, profile_url, ranking
            # return profiles
            profiles = list(set(profiles))
            self.get_profile_data_threaded(profiles)
        except Exception as e:
            logger.error(str(e))
            return False

    def get_profile_data_threaded(self, profiles):
        threads = []
        for i in range(len(profiles)):
            threads.append(gevent.spawn(self.get_profile_data, profiles[i]))
            if (i + 1) % config.THREAD_WORKERS == 0:
                gevent.joinall(threads)
            else:
                continue
        gevent.joinall(threads)

    def get_profile_data(self, profile_tuple):
        p_url = profile_tuple[1]
        rank = profile_tuple[2]
        cat = profile_tuple[0]

        resp = request(p_url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            company = self.get_company(soup)
            desc, details = self.get_desc_details(soup)
            website = self.get_website(soup)
            founded = self.get_founded(soup)
            hq = self.get_hq(soup)
            reviews = self.get_reviews(soup)
            data = [[
                name,
                company,
                website,
                desc,
                hq,
                details,
                founded,
                reviews,
                rank,
                cat,
                p_url
            ]]
            write_data(data, name)

    def get_name(self, soup):
        try:
            return soup.find('h1').get_text().replace(';', ',').strip()
        except Exception:
            return None

    def get_company(self, soup):
        try:
            return soup.find('h2').find('span').get_text().replace(';', ',').strip()
        except Exception:
            return None

    def get_desc_details(self, soup):
        try:
            details = ''
            description = ''
            for h2 in soup.select('h2'):
                txt = h2.get_text()
                if txt == f'About {self.get_name(soup)}':
                    description = h2.find_next('div', class_='base-margin-bottom').find('p').get_text().strip()

                if txt == 'Product Details':
                    lis = h2.find_next('ul', class_='check-list').select('li')
                    for li in lis:
                        det = ''
                        for i, div in enumerate(li.select('div.cell')):
                            if i == 0:
                                det += div.get_text().strip() + ': '
                            if i == 1:
                                det += ', '.join([s.strip() for s in div.get_text().strip().split('\n')]) + '\n'
                        det = det.strip(':') + '\n'
                        details = details + det.replace(';', ',')
            return description.replace(';', ',').strip(), details.replace(';', ',').strip()
        except Exception:
            return None, None

    def get_website(self, soup):
        try:
            s = soup.find('li', text=re.compile(r'www')).get_text().strip()
            if not s.startswith('http'):
                s = 'http://' + s
            return get_fld(s)
        except Exception:
            try:
                for h2 in soup.select('h2'):
                    txt = h2.get_text().strip()
                    if txt == 'Vendor Details':
                        s = h2.find_next('ul', \
                            class_='check-list').select('li')[1].get_text().strip()
                        if not s.startswith('http'):
                            s = 'http://' + s
                        return get_fld(s)
            except Exception:
                return None

    def get_founded(self, soup):
        try:
            return soup.find('li', \
                text=re.compile(r'Founded')).get_text().replace('Founded ', '').strip()
        except Exception:
            return None

    def get_hq(self, soup):
        try:
            return soup.find('li', \
                text=re.compile(r'Founded')).find_next().get_text().replace('; ', ',').strip()
        except Exception:
            return None

    def get_reviews(self, soup):
        try:
            return soup.find('a', attrs={'href':'#reviews'}).find('span').get_text().strip()
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
        'HQ',
        'Details',
        'Founded',
        'Reviews',
        'Rank',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = Capterra()
    cats = mod.get_categories()
    for cat in cats:
        mod.get_profiles(cat)


def get_data():
    main()
