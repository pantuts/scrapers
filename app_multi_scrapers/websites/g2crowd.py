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
from utils import setup_logger, request, get_sitemap_locs, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'G2Crowd'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

SITEMAP_URLS = [
    'https://www.g2crowd.com/sitemap-service_reviews.xml',
    'https://www.g2crowd.com/sitemap-software_reviews.xml'
]


class G2Crowd:
    def get_profiles(self):
        final_locs = []
        for sm in SITEMAP_URLS:
            _locs = get_sitemap_locs(sm)
            for _loc in _locs:
                # if _loc == 'https://www.g2crowd.com/' or 'competitors' in _loc:
                #     continue
                if _loc.endswith('/reviews'):
                    loc = _loc[:_loc.rindex('/') + 1]
                    loc = loc + 'details'
                    if loc not in final_locs:
                        final_locs.append(loc)
        return final_locs

    def get_data(self, url, use_std_req=False, plain_req=False):
        resp = request(url, use_std_req=use_std_req, plain_req=plain_req)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            vendor = self.get_vendor(soup)
            website = self.get_website(soup)
            desc = self.get_desc(soup)
            hq = self.get_hq(soup)
            phone = self.get_phone(soup)
            ratings = self.get_ratings(soup)
            reviews = self.get_reviews(soup)
            founded = self.get_founded(soup)
            own = self.get_ownership(soup)
            emp = self.get_employees(soup)
            cat = self.get_categories(soup)
            profile = url

            data = [[
                name, vendor, website, desc, hq, phone,
                ratings, reviews, founded, own, emp, cat, profile
            ]]
            write_data(data, name)

    def get_name(self, soup):
        try:
            return soup.find('h4').get_text().strip()
        except Exception:
            return None

    def get_vendor(self, soup):
        try:
            return soup.find('dt', text=re.compile(r'Vendor')).find_next('dd').get_text().strip()
        except Exception:
            try:
                return soup.find('th', text=re.compile(r'Vendor')).find_next('td').get_text().strip()
            except Exception:
                return None

    def get_website(self, soup):
        try:
            site = soup.find('a', {'itemprop': 'url'}).get('href')
            if not site.startswith('http'):
                site = 'http://' + site
            return get_fld(site)
        except Exception:
            return None

    def get_desc(self, soup):
        try:
            return soup.find('dt', text=re.compile(r'Description')).find_next('dd').get_text().strip()
        except Exception:
            try:
                name = self.get_name(soup)
                return soup.find('h1', text=re.compile('What is {}'.format(name))).next.next.next.get_text().replace(';', ',').strip()
            except Exception:
                return None

    def get_hq(self, soup):
        try:
            return soup.find('dt', text=re.compile(r'HQ')).find_next('dd').get_text().strip()
        except Exception:
            try:
                return soup.find('th', text=re.compile(r'HQ')).find_next('td').get_text().strip()
            except Exception:
                return None

    def get_phone(self, soup):
        try:
            return soup.find('dt', text=re.compile(r'Phone')).find_next('dd').get_text().strip()
        except Exception:
            try:
                return soup.find('th', text=re.compile(r'Phone')).find_next('td').get_text().strip()
            except Exception:
                return None

    def get_ratings(self, soup):
        try:
            return float(soup.find('div', \
                class_='rating-text').get_text().strip().split(' ')[0])
        except Exception:
            return None

    def get_reviews(self, soup):
        try:
            return int(soup.find('div', \
                text=re.compile(r'(\d)')).get_text().replace('(', '').replace(')', '').strip())
        except Exception:
            return None

    def get_founded(self, soup):
        try:
            return soup.find('dt', text=re.compile(r'Founded')).find_next('dd').get_text().strip()
        except Exception:
            try:
                return soup.find('th', text=re.compile(r'Founded')).find_next('td').get_text().strip()
            except Exception:
                return None

    def get_ownership(self, soup):
        try:
            return soup.find('dt', text=re.compile(r'Ownership')).find_next('dd').get_text().strip()
        except Exception:
            return None

    def get_employees(self, soup):
        try:
            return soup.find('dt', text=re.compile(r'Employees')).find_next('dd').get_text().strip()
        except Exception:
            try:
                return soup.find('th', text=re.compile(r'Employees')).find_next('td').get_text().strip()
            except Exception:
                return None

    def get_categories(self, soup):
        try:
            return ', '.join([li.get_text().strip() for li in \
                soup.find('h5', text=re.compile(r'Categories')).find_next('ul').find_all('li')])
        except Exception:
            try:
                return ', '.join([li.get_text().strip() for li in \
                    soup.find('th', text=re.compile(r'Categories')).find_next('ul').find_all('li')])
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
        'Vendor',
        'Website',
        'Description',
        'HQ',
        'Phone',
        'Ratings',
        'Reviews',
        'Founded',
        'Ownership',
        'Employees',
        'Category',
        'Profile'
    ]])


def main2():
    mod = G2Crowd()
    profiles = [s.strip() for s in open('data/logs/g2crowd.txt').readlines() if s.strip()]
    for profile in profiles:
        mod.get_data(profile, use_std_req=True, plain_req=True)


def main():
    csv_header()
    mod = G2Crowd()
    profiles = mod.get_profiles()
    for profile in profiles:
        mod.get_data(profile, use_std_req=True, plain_req=True)


def get_data(rescrape=False):
    if rescrape:
        main2()
    else:
        main()
