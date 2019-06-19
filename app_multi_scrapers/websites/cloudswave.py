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
NAME = 'CloudsWave'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

SITEMAP_URL = 'https://cloudswave.com/sitemaps/sitemap-products-https.xml'


class CloudsWave:
    def get_profiles(self):
        logger.info(SITEMAP_URL)
        final_locs = get_sitemap_locs(SITEMAP_URL)
        return final_locs

    def get_data(self, url):
        logger.info(url)
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            if not name:
                return False
            website = self.get_website(soup)
            desc = self.get_description(soup)
            features = self.get_features(soup)
            platforms = self.get_platforms(soup)
            rating = self.get_rating(soup)
            reviews = self.get_reviews(soup)
            category = self.get_category(soup)
            profile = url

            data = [[
                name,
                website,
                desc,
                features,
                platforms,
                rating,
                reviews,
                category,
                profile
            ]]
            write_data(data, name)

    def get_name(self, soup):
        try:
            return soup.find('h1').find('strong').get_text().strip()
        except:
            return ''

    def get_website(self, soup):
        try:
            href = unquote(soup.find('a', attrs={'href': re.compile(r'view_website')}).get('href'))
            url = re.findall(r'url=(.+?)&product', href)[0]
            return get_fld(url)
        except:
            return ''

    def get_category(self, soup):
        try:
            return ', '.join([span.get_text() for span in soup.find('i', class_='fa-th-large').find_next('div').find_all('span')])
        except:
            return ''

    def get_description(self, soup):
        try:
            return soup.find_all('i', class_='fa-info-circle')[1].find_next('p').get_text().strip()
        except:
            return ''

    def get_features(self, soup):
        try:
            specs = soup.select('div.specifications')
            for div in specs:
                divs = div.select('div')
                for d in divs:
                    htag = d.find(re.compile(r'h'))
                    if htag:
                        h = htag.get_text().strip() or None
                        if h:
                            if h == 'Key Features':
                                lis = htag.find_next('div').find_all('li')
                                features = ', '.join([li.get_text().strip() for li in lis])
                                return features
        except:
            return ''

    def get_rating(self, soup):
        try:
            r = soup.find('span', attrs={'itemprop': 'ratingValue'}).get_text().strip()
            if r == 'TBD':
                return ''
            return r
        except:
            return ''

    def get_reviews(self, soup):
        try:
            return soup.find('meta', attrs={'itemprop': 'ratingCount'}).get('content')
        except:
            return ''

    def get_platforms(self, soup):
        try:
            return (', ').join([li.get_text() for li in \
                soup.find('i', class_='icon-devices').find_next('div').find_all('li')])
        except:
            return ''


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
        'Platforms',
        'Rating',
        'Reviews',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = CloudsWave()
    profiles = mod.get_profiles()
    for profile in profiles:
        mod.get_data(profile)


def get_data():
    main()
