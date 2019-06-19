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
NAME = 'FeaturedCustomer'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

SITEMAP_URL = 'https://www.featuredcustomers.com/sitemap_vendors.xml'


class FeatureCustomers:
    def get_profiles(self):
        logger.info(f'Getting profiles - {SITEMAP_URL}')
        final_locs = get_sitemap_locs(SITEMAP_URL)
        return final_locs

    def get_data(self, url):
        logger.info(f'Getting source - {url}')
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            if not name:
                return False
            website = self.get_website(soup)
            hq = self.get_address(soup)
            phone = self.get_phone(soup)
            desc = self.get_description(soup)
            rating = self.get_rating(soup)
            reviews = self.get_reviews(soup)
            customers = self.get_customers(soup)
            category = self.get_category(soup)
            profile = url

            data = [[
                name,
                website,
                desc,
                hq,
                phone,
                customers,
                rating,
                reviews,
                category,
                profile
            ]]
            write_data(data, name)

    def get_name(self, soup):
        try:
            return soup.find('h3', attrs={'itemprop': 'name'}).get_text().strip()
        except Exception:
            return None

    def get_website(self, soup):
        try:
            url = soup.find('span', attrs={'itemprop': 'url'}).get_text().strip()
            if not url.startswith('http'):
                url = 'http://' + url
            return get_fld(url)
        except Exception:
            return None

    def get_address(self, soup):
        try:
            locality = soup.find('span', attrs={'itemprop': 'addressLocality'})
            if locality:
                locality = locality.get_text().strip()
            region = soup.find('span', attrs={'itemprop': 'addressRegion'})
            if region:
                region = region.get_text().strip()
            address = ', '.join(list(filter(None, [locality, region])))
            return address
        except Exception:
            return None

    def get_phone(self, soup):
        try:
            return soup.find('span', attrs={'itemprop': 'telephone'}).get_text().strip()
        except Exception:
            return None

    def get_category(self, soup):
        try:
            return soup.find('span', attrs={'itemprop': 'additionalType'}).get_text().strip()
        except Exception:
            return None

    def get_description(self, soup):
        try:
            return soup.find('div', class_='mble_domo_desc_inner').find('p').get_text().replace(';', ',').strip()
        except Exception:
            return None

    def get_rating(self, soup):
        try:
            return soup.find('div', class_='overallrating').get_text().strip()
        except Exception:
            return None

    def get_reviews(self, soup):
        try:
            return soup.find('span', attrs={'itemprop': 'reviewCount'}).get_text().strip()
        except Exception:
            return None

    def get_customers(self, soup):
        try:
            return ', '.join([img.get('alt').strip() for img in soup.find('div', class_='companies_using_logo').find_all('img')])
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
        'HQ',
        'Phone',
        'Customers',
        'Rating',
        'Reviews',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = FeatureCustomers()
    profiles = mod.get_profiles()
    for profile in profiles:
        mod.get_data(profile)


def get_data():
    main()
