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
NAME = 'USA_LOCAL_GOV_NEWYORK'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

URL = 'https://www.ny.gov/services/nygov/search?draw=2&columns[0][data]=markup'
URL += '&columns[0][name]=&columns[0][searchable]=true&columns[0][orderable]=false'
URL += '&columns[0][search][value]=&columns[0][search][regex]=false&order[0][column]=0'
URL += '&order[0][dir]=asc&start={}&length=10&search[value]=&search[regex]=false'
URL += '&entity_types[0]=taxonomy_term&bundles[0]=county&keywords=&searchgroup_id=county&searcher_id=county'


class UsaLocalGov:
    def get_counties(self):
        counties = []
        start = 0
        error_count = 0
        while True:
            if error_count == 3:
                return counties
            url = URL.format(start)
            resp = request(url)
            if resp:
                try:
                    json_data = resp.json()
                    data = json_data.get('data')
                    if not data:
                        return counties
                    for d in data:
                        soup = BeautifulSoup(d.get('markup'), 'lxml')
                        counties.append(soup.find('a').get('href'))
                    start = start + 10
                except Exception:
                    error_count = error_count + 1

    def get_data(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')

            name = soup.find('h1').get_text().strip()
            desc = None
            try:
                desc = '\n'.join([p.get_text().strip() for p in soup.find('div', class_='content').find_all('p')])
            except Exception:
                pass
            addr = None
            try:
                addr = soup.find('p', class_='address').get_text().strip()
            except Exception:
                pass
            phone = None
            try:
                phone = soup.find('p', class_='phone').get_text().strip()
            except Exception:
                pass
            population = None
            try:
                population = soup.find('label', text=re.compile(r'Population')).find_next('p').get_text().strip()
            except Exception:
                pass
            founded = None
            try:
                founded = soup.find('label', text=re.compile(r'Founded')).find_next('p').get_text().strip()
            except Exception:
                pass
            area = None
            try:
                area = soup.find('label', text=re.compile(r'Area')).find_next('p').get_text().strip()
            except Exception:
                pass
            officials = None
            try:
                officials = '\n'.join([p.get_text().strip() for p in \
                                soup.find('div', text=re.compile(r'Elected Officials')).find_previous('div', \
                                {'about':re.compile(r'/field-collection/field-chapters/')}).find('div', \
                                class_='field--name-field-body').find_all('p')])
            except Exception:
                pass
            municipalities = None
            try:
                municipalities = '\n'.join([a.get_text().strip() for a in \
                                    soup.find('div', text=re.compile(r'Municipalities')).find_previous('div', \
                                    {'about':re.compile(r'/field-collection/field-chapters/')}).find('div', \
                                    class_='field--name-field-body').find_all('a')])
            except Exception:
                pass

            data = [[
                name,
                desc,
                addr,
                phone,
                area,
                founded,
                population,
                officials,
                municipalities,
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
        'Description',
        'Address',
        'Phone',
        'Area (Sq Miles)',
        'Founded',
        'Population',
        'Elected Officials',
        'Municipalities'
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
