#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import os
import re
import requests
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_fld
from utils import setup_logger, request, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'GetApp'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

MAIN_URL = 'https://www.getapp.com'
BROWSE_URL = 'https://www.getapp.com/browse'


class GetApp:
    def get_categories(self):
        resp = request(BROWSE_URL)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            return [MAIN_URL + a.get('href') for a in [h4.find('a') for h4 in soup.find_all('h4')] if a]
        return []

    def get_profiles(self, cat):
        profiles = []

        pagination = True
        page = 1
        page_str = '?page={}'
        page_err = 0
        while pagination:
            resp = request(cat + page_str.format(page))
            if resp:
                soup = BeautifulSoup(resp.text, 'lxml')
                try:
                    if 'No results found' in str(soup) or page_err == 3:
                        pagination = False

                    profiles.extend([MAIN_URL + a.get('href') for a in soup.find_all('a', class_='serp-read-more')])
                except Exception:
                    return False
            else:
                page_err = page_err + 1
                if page_err == 3:
                    pagination = False
            page = page + 1
        profiles = list(set(profiles))
        return profiles

    def get_data(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            website = self.get_website(soup)
            desc = self.get_description(soup)
            pricing = self.get_pricing(soup)
            rating = self.get_rating(soup)
            reviews = self.get_reviews(soup)
            feat = self.get_features(soup)
            supp_cnt = self.get_supported_countries(soup)
            cat = self.get_category(soup)
            sub_cat = self.get_sub_category(soup)

            data = [[
                name,
                website,
                desc,
                pricing,
                rating,
                reviews,
                feat,
                supp_cnt,
                cat,
                sub_cat,
                url
            ]]
            write_data(data, name)

    def get_name(self, soup):
        try:
            s = soup.find('h2').get_text().strip().replace(';', '')
            return s
        except Exception:
            return None

    def get_description(self, soup):
        try:
            s = soup.find('div', attrs={'itemprop': 'description'}).get_text().strip()
            return s.replace(';', '')
        except Exception:
            return None

    def get_website(self, soup):
        try:
            s = soup.find('span', {'itemprop': 'author'}).find_next().find_next().get_text().strip()
            if not s.startswith('http'):
                s = 'http://' + s
            return get_fld(s)
        except Exception:
            try:
                s = MAIN_URL + soup.find('a', text=re.compile(r'Visit Website')).get('href')
                resp = request(s)
                external_url = re.findall(r'location\.replace.+?"(.+?)"', resp.text)[0]
                if 'external_click_ga' in external_url:
                    r = requests.head(external_url)
                    url = r.headers['Location']
                    return get_fld(url)
                return get_fld(external_url)
            except Exception:
                return None

    def get_pricing(self, soup):
        try:
            s = soup.find('h4', text=re.compile(r'Pricing')).find_next('div')
            s.find('div', text='Starting from').replaceWith('')
            return s.get_text().strip()
        except Exception:
            return None

    def get_rating(self, soup):
        try:
            s = soup.find('span', attrs={'itemprop': 'ratingValue'}).get_text().strip()
            return s
        except Exception:
            return None

    def get_reviews(self, soup):
        try:
            s = soup.find('span', attrs={'itemprop': 'ratingCount'}).get_text().strip()
            return s
        except Exception:
            return None

    def get_features(self, soup):
        try:
            s = []
            div = soup.find('h4', text=re.compile(r'Key features')).find_next('div')
            for li in div.find_all('li'):
                s.append(li.get_text().strip().replace(';', ''))
            return '\n'.join(s)
        except Exception:
            return None

    def get_supported_countries(self, soup):
        try:
            s = soup.find('h4', text='Markets').find_next('div').get_text().strip()
            s = str(re.sub('and [0-9] other markets', '', s))
            return ', '.join([ss.strip() for ss in s.split(',')])
        except Exception:
            return None

    def get_category(self, soup):
        try:
            return soup.find('span', attrs={'itemprop': 'title'}).get_text().strip()
        except Exception:
            return None

    def get_sub_category(self, soup):
        try:
            return ', '.join([s.get_text() for s in soup.find_all('span', {'itemprop': 'applicationSubCategory'})])
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
        'Pricing',
        'Rating',
        'Reviews',
        'Features',
        'Supported Countries',
        'Category',
        'SubCategory',
        'Profile'
    ]])


def main():
    csv_header()
    mod = GetApp()
    cats = mod.get_categories()
    for cat in cats:
        profiles = mod.get_profiles(cat)
        for profile in profiles:
            mod.get_data(profile)


def get_data():
    main()
