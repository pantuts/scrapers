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
from utils import setup_logger, request, get_sitemap_locs, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'Built_In_Colorado'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

SITEMAPS = [
    'https://www.builtincolorado.com/sitemaps/2/sitemap.xml',
    'https://www.builtincolorado.com/sitemaps/3/sitemap.xml',
    'https://www.builtincolorado.com/sitemaps/4/sitemap.xml'
]


class BuiltInColorado:
    def get_profiles(self):
        final_locs = []
        for sitemap in SITEMAPS:
            logger.info(sitemap)
            _locs = get_sitemap_locs(sitemap)
            for _loc in _locs:
                if _loc.startswith('https://www.builtincolorado.com/company/'):
                    final_locs.append(_loc)
        final_locs = list(set(final_locs))
        return final_locs

    def get_data(self, url):
        resp = request(url, use_headers=False)
        if resp:
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'lxml')

            name = url.split('/')[-1].title()
            desc = self.get_description(soup)
            website = self.get_website(soup)
            hq = self.get_hq(soup)
            founded = self.get_founded(soup)
            employees = self.get_employees(soup)
            com_type = self.get_type(soup)
            cat = self.get_category(soup)

            data = [[
                name,
                website,
                desc,
                hq,
                founded,
                employees,
                com_type,
                cat,
                url
            ]]
            write_data(data, name)

    def get_description(self, soup):
        try:
            return soup.find('div', class_='description').get_text().strip().replace(';', ',')
        except Exception:
            return None

    def get_website(self, soup):
        try:
            return get_fld(soup.find('div', class_='field_company_website').find('a').get('href'))
        except Exception:
            return None

    def get_hq(self, soup):
        try:
            s = soup.find('div', class_='company-card-info').find('div', class_='col-1').find('div').get_text().strip()
            if s == ',':
                return None
            return s
        except Exception:
            return None

    def get_founded(self, soup):
        try:
            return soup.find('div', class_='field_year_founded').find('time').get_text().strip()
        except Exception:
            return None

    def get_employees(self, soup):
        try:
            s = soup.find_all('div', class_='field_local_employees')[-1].get_text()
            s = s.replace('Total Employees:', '').strip()
            s = s.replace('Local Employees:', '').strip()
            s = s.replace(',', '').strip()
            return s
        except Exception:
            return None

    def get_type(self, soup):
        try:
            return soup.find('div', class_='field_company_type').find('div', class_='label').get_text().strip()
        except Exception:
            return None

    def get_category(self, soup):
        try:
            return soup.find('div', class_='field_company_type').find('div', class_='item').get_text().strip()
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
        'Founded',
        'Employees',
        'Type',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = BuiltInColorado()
    profiles = mod.get_profiles()
    for url in profiles:
        mod.get_data(url)


def get_data():
    main()
