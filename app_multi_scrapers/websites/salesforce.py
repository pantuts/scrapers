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

# import gevent
# import gevent.monkey
# if 'threading' in sys.modules:
#     del sys.modules['threading']

from bs4 import BeautifulSoup
from datetime import datetime
from utils import setup_logger, request, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'Salesforce'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

APPS_URL = 'https://appexchange.salesforce.com/results?pageNo={}'
APPS_AJAX_URL = 'https://appexchange.salesforce.com/appxstore'


class SalesforceApp:
    def __init__(self):
        self.form_data = None
        self.apps_done = []

    def get_form_data(self, soup):
        try:
            form_id = soup.find('form', {'action': '/appxstore'}).get('id')
            view_states = [(inp.get('name'), inp.get('value')) for inp in soup.find('span', id='ajax-view-state-page-container').find_all('input', {'type': 'hidden'})]
            loadmore = soup.find('script', text=re.compile(r'loadMore\=')).get('id')
            form_data = {
                'AJAXREQUEST': '_viewRoot',
                form_id: form_id
            }
            for vs in view_states:
                form_data.update({vs[0]: vs[1]})
            form_data.update({loadmore: loadmore})
            self.form_data = form_data
        except Exception:
            pass

    def get_profiles(self):
        form_data_done = False
        page = 1
        pagination = True

        while pagination:
            if not form_data_done:
                resp = request(APPS_URL.format(page))
            else:
                h = {
                    'Accept': '*/*',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive'
                }
                resp = request(APPS_AJAX_URL, req_type='post', data=self.form_data, headers=h, data_dumps=True)
            if resp:
                soup = BeautifulSoup(resp.text, 'lxml')

                # if not form_data_done:
                self.get_form_data(soup)
                form_data_done = True
                if not self.form_data:
                    logger.error('ViewStates not found!')
                    break

                if not soup.find('span', text='Show More'):
                    pagination = False

                with open('test.html', 'w') as f:
                    f.write(str(soup))

                profiles = [a.get('href') for a in \
                            soup.select('div#j_id0:AppxLayout:listings a.appx-tile.appx-tile-app.tile-link-click, div#j_id0:AppxLayout:newRowsListings a.appx-tile.appx-tile-app.tile-link-click')]
                profiles = list(filter(lambda x: x not in self.apps_done, profiles))
                self.apps_done.extend(profiles)

                for profile in profiles:
                    self.get_data(profile)

                # threads = []
                # for i in range(len(profiles)):
                #     threads.append(gevent.spawn(self.get_data, profiles[i]))
                #     if (i + 1) % config.THREAD_WORKERS == 0:
                #         gevent.joinall(threads)
                #     else:
                #         continue
                # gevent.joinall(threads)
            # page = page + 1

    def get_data(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            if not name:
                return False
            desc = self.get_description(soup)
            rating = self.get_rating(soup)
            reviews = self.get_reviews(soup)
            listed = self.get_listed_on(soup)
            latest = self.get_latest_release(soup)
            cat = self.get_categories(soup)

            data = [[
                name,
                desc,
                rating,
                reviews,
                listed,
                latest,
                cat,
                url
            ]]
            write_data(data, name)
            self.apps_done.append(url)

    def get_name(self, soup):
        try:
            return soup.find('p', class_='appx-page-header-root').get_text().strip()
        except Exception:
            return None

    def get_description(self, soup):
        try:
            return soup.find('div', class_='appx-detail-section-description').get_text().strip()
        except Exception:
            return None

    def get_rating(self, soup):
        try:
            r = soup.find('span', class_=re.compile(r'appx-rating-stars-[0-9]')).get('class')[-1].split('-')[-1]
            rating = r[0] if r[-1] == '0' else r[0] + '.' + r[-1]
            if rating in ['0.0', '0.', '0']:
                rating = None
            return rating
        except Exception:
            return None

    def get_reviews(self, soup):
        try:
            r = soup.find('span', class_='appx-rating-amount').get_text().strip()
            return re.sub('\(|\)', '', r)
        except Exception:
            return None

    def get_listed_on(self, soup):
        try:
            return soup.find('div', class_='appx-detail-section-first-listed').find_all('p')[-1].get_text().strip()
        except Exception:
            return None

    def get_latest_release(self, soup):
        try:
            return soup.find('div', class_='appx-detail-section-first-listed').find_all('p')[-1].get_text().strip()
        except Exception:
            return None

    def get_pricing(self, soup):
        try:
            return soup.find('p', class_='appx-pricing-detail-header').get_text().strip()
        except Exception:
            return None

    def get_categories(self, soup):
        try:
            return ', '.join([a.get_text().strip() for a in soup.find('div', class_='appx-headline-details-categories').find_all('a')])
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
        'Description',
        'Rating',
        'Reviews',
        'Listed On',
        'Latest Release',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = SalesforceApp()
    mod.get_profiles()


def get_data():
    main()
