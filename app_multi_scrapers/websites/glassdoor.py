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
from utils import setup_logger, request, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'Glassdoor'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

MAIN_URL = 'https://www.glassdoor.com'
BROWSE_URL = 'https://www.glassdoor.com/sitedirectory/company-jobs.htm'


class Glassdoor:
    def get_categories(self):
        try:
            resp = request(BROWSE_URL)
            soup = BeautifulSoup(resp.text, 'lxml')
            return [MAIN_URL + a.get('href') for a in \
                    soup.find_all('a', {'href': re.compile(r'/sitedirectory/company-jobs/')})]
        except Exception:
            return []

    def get_profiles(self, cat):
        try:
            profiles = []
            resp = request(cat)
            soup = BeautifulSoup(resp.text, 'lxml')
            for li in soup.select('ol.catList li'):
                a = li.find('a', text='Reviews')
                if a:
                    _tmp = a.get('href').rpartition('/')
                    profiles.append(MAIN_URL + '/Overview/' + 'Working-at-' + _tmp[-1].replace('Reviews-', 'EI_I'))
            return profiles
        except Exception:
            return []

    def get_data(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            site = self.get_website(soup)
            desc = self.get_desc(soup)
            hq = self.get_hq(soup)
            founded = self.get_founded(soup)
            comp_type = self.get_type(soup)
            competitors = self.get_competitors(soup)
            rev = self.get_revenue(soup)
            emp = self.get_employees(soup)
            rating = self.get_rating(soup)
            reviews = self.get_reviews(soup)
            cat = self.get_category(soup)

            data = [[
                name,
                site,
                desc,
                hq,
                founded,
                comp_type,
                competitors,
                rev,
                emp,
                rating,
                reviews,
                cat,
                url
            ]]
            write_data(data, name)

    def get_name(self, soup):
        try:
            return soup.find('h1').get_text().strip()
        except Exception:
            return None

    def get_website(self, soup):
        try:
            s = soup.find('span', class_='website').find('a').get('href').strip()
            if not s.startswith('http'):
                s = 'http://' + s
            return get_fld(s)
        except Exception:
            return None

    def get_desc(self, soup):
        try:
            return soup.find('div', class_='empDescription').get('data-full').replace(';', ',').strip()
        except Exception:
            return None

    def get_hq(self, soup):
        try:
            return soup.find('label', text='Headquarters').find_next().get_text().strip()
        except Exception:
            return None

    def get_founded(self, soup):
        try:
            return soup.find('label', text='Founded').find_next().get_text().strip()
        except Exception:
            return None

    def get_type(self, soup):
        try:
            return soup.find('label', text='Type').find_next().get_text().strip()
        except Exception:
            return None

    def get_competitors(self, soup):
        try:
            return soup.find('label', text='Competitors').find_next().get_text().strip()
        except Exception:
            return None

    def get_revenue(self, soup):
        try:
            return soup.find('label', text='Revenue').find_next().get_text().strip()
        except Exception:
            return None

    def get_employees(self, soup):
        try:
            return soup.find('label', text='Size').find_next().get_text().replace('employees', '').strip()
        except Exception:
            return None

    def get_rating(self, soup):
        try:
            return soup.find('div', class_='ratingNum').get_text().strip()
        except Exception:
            return None

    def get_reviews(self, soup):
        try:
            return ''.join(re.findall('([0-9,])', \
                soup.find('div', class_='multipleReviews').find_next('a', class_='moreBar').get_text().strip())).replace(',', '')
        except Exception:
            return None

    def get_category(self, soup):
        try:
            return soup.find('label', text='Industry').find_next().get_text().replace('employees', '').strip()
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
        'Company Type',
        'Competitors',
        'Revenue',
        'Employees',
        'Rating',
        'Reviews',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = Glassdoor()
    cats = mod.get_categories()
    for cat in cats:
        profiles = mod.get_profiles(cat)
        for profile in profiles:
            mod.get_data(profile)


def get_data():
    main()
