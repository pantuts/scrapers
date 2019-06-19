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
from utils import setup_logger, request, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'StartupsList'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

MAIN_URL = 'http://www.startups-list.com/'


class StartupsList:
    def get_countries(self):
        countries_url = []
        resp = request(MAIN_URL)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            links = soup.select('.citylink')
            for link in links:
                url = link.get('href')
                country = link.find('h3').get_text().strip()
                countries_url.append((url, country))
        return countries_url

    def get_data(self, url, country):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            startups = soup.select('.startup')
            for card in startups:
                name = card.get('data-name').replace(';', ',').strip()
                desc = card.find('p')
                if desc:
                    desc = desc.get_text().replace(';', ',').strip()
                try:
                    site = card.find('i', class_='fa-globe').find_previous().get('href').strip()
                    if not site.startswith('http'):
                        site = 'http://' + site
                    site = get_fld(site)
                except:
                    site = None
                try:
                    fb = card.find('i', class_='fa-facebook-square').find_previous().get('href').strip()
                except:
                    fb = None
                try:
                    tw = card.find('i', class_='fa-twitter').find_previous().get('href').strip()
                except:
                    tw = None

                data = [[name, site, desc, fb, tw, country]]
                write_data(data, name)


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
        'Facebook',
        'Twitter',
        'Country/City'
    ]])


def main():
    csv_header()
    mod = StartupsList()
    countries = mod.get_countries()
    for url_country in countries:
        mod.get_data(url_country[0], url_country[1])


def get_data():
    main()
