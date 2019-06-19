#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import json
import os
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_fld
from utils import setup_logger, request, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'USA_LOCAL_GOV_OHIO'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

URL = 'https://ohio.gov/wps/portal/gov/site/government/resources/counties'


class UsaLocalGov:
    def get_data(self):
        data = []
        resp = request(URL)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            try:
                data_list = json.loads(soup.find('div', id='js-placeholder-json-data').get_text().strip())
                data_list = sorted(data_list.get('data')[2:])
            except Exception:
                data_list = []

            if not data_list:
                return False

            county = None
            official = None
            range = None
            fname = None
            mname = None
            lname   = None
            addr = None
            pobox = None
            city = None
            state = None
            zip = None
            url = None
            for d in data_list:
                if not d or len(d) < 10:
                    continue
                county = d[0]
                official = d[1]
                range = d[2]
                fname = d[3]
                mname = d[4]
                lname = d[5]
                addr = d[6]
                pobox = d[7]
                city = d[8]
                state = d[9]
                zip = d[10]
                try:
                    url = get_fld(d[11])
                except Exception:
                    pass

                data.append([
                    county,
                    official,
                    range,
                    fname,
                    mname,
                    lname,
                    addr,
                    pobox,
                    city,
                    state,
                    zip,
                    url
                ])
        for d in data:
            write_data([d], d[0])


def write_data(data, name=None):
    done = csv_utils.write_csv(CSV_FNAME, data, NOW)
    if name:
        if done:
            logger.info(f'[CSV] Done >> {name}')


def csv_header():
    write_data([[
        'Name',
        'Official',
        'Range',
        'First Name',
        'Middle Name',
        'Last Name',
        'Address',
        'PO Box',
        'City',
        'State',
        'Zip',
        'Website'
    ]])


def main():
    csv_header()
    mod = UsaLocalGov()
    mod.get_data()


def get_data():
    main()
