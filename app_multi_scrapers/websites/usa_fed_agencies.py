#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import os
import re
import string
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_fld
from utils import setup_logger, request, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'USA_FEDERAL_AGENCIES'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

URLS = ['https://www.usa.gov/federal-agencies/' + i for i in string.ascii_lowercase]


class UsaFedAgencies:
    def get_profiles(self):
        profiles = []
        for url in URLS:
            logger.info(url)
            resp = request(url)
            if resp:
                soup = BeautifulSoup(resp.text, 'lxml')
                profiles.extend(['https://www.usa.gov' + a.get('href') for a in soup.select('ul.one_column_bullet li a')])
        return profiles

    def get_data(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')

            name = soup.find('h1').get_text().replace(';', ',').strip()
            website = None
            try:
                website = get_fld(soup.find('h3', text=r'Website:').find_next('p').find('a').get('href'))
            except Exception:
                pass
            desc = None
            try:
                desc = soup.find('h1').find_next('p').get_text().replace(';', ',').strip()
            except Exception:
                pass
            contact_site = None
            try:
                contact_site = soup.find('a', text=re.compile(r'Contact the')).get('href').strip()
            except Exception:
                pass
            addr = None
            try:
                addr = [i.strip() for i in soup.find('p', class_='street-address').get_text().strip().split('\n') if i.strip()]
                addr = ', '.join(addr[:-2]) + ' ' + ' '.join(addr[-2:])
            except Exception:
                pass
            email = None
            try:
                email = soup.find('a', href=re.compile(r'mailto')).get_text().strip()
            except Exception:
                pass
            phone = None
            try:
                phone = soup.find('a', href=re.compile(r'tel')).get_text().strip()
            except Exception:
                pass
            phone_toll_free = None
            try:
                phone_toll_free = soup.find('h3', text=re.compile(r'Toll Free')).find_next('a', href=re.compile(r'tel')).get_text().strip()
            except Exception:
                pass
            branch = None
            try:
                branch = soup.find('h3', text=re.compile(r'Government branch')).find_next('p').get_text().strip()
            except Exception:
                pass

            data = [[
                name,
                website,
                desc,
                addr,
                contact_site,
                email,
                phone,
                phone_toll_free,
                branch,
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
        'Contact Site',
        'Email',
        'Phone',
        'Phone Toll Free',
        'Branch',
        'Profile'
    ]])


def main():
    csv_header()
    mod = UsaFedAgencies()
    profiles = mod.get_profiles()
    for url in profiles:
        mod.get_data(url)


def get_data():
    main()
