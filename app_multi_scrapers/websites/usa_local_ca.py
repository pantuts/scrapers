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
NAME = 'USA_LOCAL_GOV_CALIFORNIA'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

URL = 'http://www.counties.org/county-websites-profile-information'


class UsaLocalGov:
    def get_counties(self):
        counties = []
        resp = request(URL)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            counties = list(set(['http://www.counties.org' + a.get('href') \
                            for a in soup.find_all('a', href=re.compile(r'/county-profile/'))]))
        return counties

    def get_data(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')

            name = soup.find('div', id='main').find('h1').find('span', class_='title').get_text().strip()
            website = None
            try:
                website = get_fld(soup.find('div', id='node-sidebar').find('div', \
                                class_='node-links').find('li', class_=re.compile('link-related-www')).find('a').get('href').strip())
            except Exception:
                pass
            desc = None
            try:
                desc = soup.find('strong', \
                            text=re.compile(name.strip(' County').upper())).previous('p').previous_element.get_text().replace(';', ',').strip()
            except Exception:
                pass
            addr = None
            try:
                addr = soup.find('div', class_='field-address').get_text().strip()
            except Exception:
                pass
            population = None
            try:
                population = soup.find('strong', text=re.compile(r'OPULATION')).next.next.strip()
            except Exception:
                pass
            inc_date = None
            try:
                inc_date = soup.find('strong', text=re.compile(r'INCORPORATION DATE')).next.next.strip()
            except Exception:
                pass
            boards = None
            try:
                boards = soup.find('strong', text=re.compile(r'BOARD')).find_parent().find_parent().find_next('ul').get_text().strip()
            except Exception:
                pass
            form_of_gov = None
            try:
                form_of_gov = soup.find('strong', text=re.compile(r'FORM OF GOVERNMENT')).next.next.strip()
            except Exception:
                pass

            data = [[
                name,
                website,
                desc,
                addr,
                population,
                inc_date,
                boards,
                form_of_gov,
                url
            ]]
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
        'Address',
        'Population',
        'Incorporation Date',
        'Board of Supervisors',
        'Form of Government',
        'Profile'
    ]])


def main():
    csv_header()
    mod = UsaLocalGov()
    counties = mod.get_counties()
    for url in counties:
        mod.get_data(url)


def get_data():
    main()
