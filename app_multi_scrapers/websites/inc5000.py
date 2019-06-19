#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import config
import os
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_fld
from utils import setup_logger, request, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'Inc5000'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')
NOW_YEAR = int(datetime.strftime(datetime.now(), '%Y')) - 1

MAIN_URL = 'https://www.inc.com'
LIST_URL = 'https://www.inc.com/inc5000list/json/inc5000_{}.json'
PROFILE_URL = 'https://www.inc.com/rest/inc5000company/{}/{}'


class Inc5000:
    def __init__(self, year):
        self.year = year

    def get_ids(self):
        companies = []
        resp = request(LIST_URL.format(self.year), headers={'Accept': config.ACCEPT.get('json')})
        if resp:
            jsn = resp.json()
            for entry in jsn:
                company_id = entry.get('id')
                growth = entry.get('growth')
                rev = entry.get('revenue')
                cat = entry.get('industry')
                emps = entry.get('workers')
                url_id = entry.get('url')
                companies.append({
                    company_id: {
                        'growth': growth,
                        'revenue': rev,
                        'category': cat,
                        'employees': emps,
                        'url_id': url_id
                    }
                })
        return companies

    def get_data(self, companies):
        for entry in companies:
            for key, val in entry.items():
                company_id = key
                resp = request(PROFILE_URL.format(company_id, val.get('url_id')), headers={'Accept': config.ACCEPT.get('json')})
                if resp:
                    jsn = resp.json()
                    name = jsn.get('ifc_company')
                    if not name:
                        continue
                    rev_prev = jsn.get('current_ify_revenue_previous')
                    rank = jsn.get('current_ify_rank')
                    profile = f'{MAIN_URL}/profile/' + jsn.get('ifc_filelocation')

                    website = None
                    _site = jsn.get('ifc_url')
                    if _site:
                        try:
                            if not _site.startswith('http'):
                                _site = 'http://' + _site
                            website = get_fld(_site)
                        except:
                            pass

                    desc = None
                    _desc = jsn.get('ifc_business_description')
                    if _desc:
                        try:
                            desc = BeautifulSoup(_desc, 'lxml').find('p').get_text().strip()
                        except Exception:
                            desc = BeautifulSoup(_desc, 'lxml')
                            desc.find('h2').replaceWith('')
                            desc = desc.get_text().strip()

                    addr = jsn.get('ifc_address')
                    city = jsn.get('ifc_city')
                    state = jsn.get('ifc_state')
                    country = jsn.get('country')
                    address = ', '.join(list(filter(None, [addr, city, state, country])))

                    founded = jsn.get('ifc_founded')
                    fname = jsn.get('ifc_primary_first_name')
                    lname = jsn.get('ifc_primary_first_name')
                    primary_contact = ' '.join(list(filter(None, [fname, lname])))
                    primary_email = jsn.get('ifc_primary_email')
                    primary_phone = jsn.get('ifc_primary_phone')
                    ceo = jsn.get('ifc_ceo_name')
                    ceo_email = jsn.get('ifc_ceo_email')
                    ceo_phone = jsn.get('ifc_ceo_phone')

                    data = [[
                        name, website, desc, address, rank,
                        val.get('growth'), val.get('revenue'), rev_prev,
                        founded,
                        primary_contact, primary_email, primary_phone,
                        ceo, ceo_email, ceo_phone,
                        val.get('employees'), val.get('category'), profile
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
        'HQ',
        'Rank',
        'Growth',
        'Revenue',
        'Prev Revenue',
        'Founded',
        'Contact',
        'Email',
        'Phone',
        'CEO',
        'CEO Email',
        'CEO Phone',
        'Employees',
        'Category',
        'Profile'
    ]])


def main(year):
    if not year:
        year = NOW_YEAR
    else:
        year = int(year)
    csv_header()
    mod = Inc5000(year)
    companies = mod.get_ids()
    mod.get_data(companies)


def get_data(year=None):
    main(year)
