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
NAME = 'SaasMax'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

APPS_URL = 'https://www.saasmax.com/apps'
APPS_URL_OFFSET = 'https://www.saasmax.com/apps?offset={}&initialOffset={}'
APP_URL_DETAIL = 'https://www.saasmax.com/appDetail/{}'
APP_PROFILE = 'https://www.saasmax.com/marketplace#!/profile/{}'


class SaasMax:
    def get_data(self):
        initial_offset = None
        offset = None
        max = None
        total = None
        pagination = True
        apps_done = []

        while pagination:
            url = APPS_URL
            if initial_offset:
                url = APPS_URL_OFFSET.format(offset, initial_offset)
            resp = request(url)
            if resp:
                try:
                    json_data = resp.json()
                    apps = json_data.get('apps')
                    pgntn = json_data.get('pgntn')
                except Exception:
                    apps = []

                if not apps:
                    break

                if not total:
                    total = pgntn.get('total')
                if not max:
                    max = pgntn.get('max')
                if not initial_offset:
                    initial_offset = pgntn.get('initialOffset')
                offset = pgntn.get('offset') + max

                for app in apps:
                    app_id = app.get('id')
                    if app_id in apps_done:
                        continue
                    apps_done.append(app_id)
                    profile = APP_PROFILE.format(app_id)

                    name = app.get('name')
                    vendor = app.get('vendor')
                    website = app.get('url')
                    if website:
                        if not website.startswith('http'):
                            website = 'http://' + website
                        website = get_fld(website)
                    desc = app.get('description').strip().replace(';', ',')
                    cat = app.get('appTypeLabel')

                    target_customer = None
                    customer_size = None
                    licensing_terms = None
                    country = None
                    support_phone = None
                    support_phone_hours = None
                    resp = request(APP_URL_DETAIL.format(app_id))
                    if resp:
                        try:
                            detail = resp.json().get('detail')
                        except Exception:
                            detail = None
                        if detail:
                            target_customer = detail.get('trgtCstmrDesc')
                            if target_customer:
                                target_customer = target_customer.strip().replace(';', ',')
                            customer_size = detail.get('cstmrSzCsv')
                            if customer_size:
                                customer_size = ', '.join([s[2:] for s in customer_size.split(',')])
                            licensing_terms = detail.get('lcnsngTrms')
                            country = detail.get('cntry')
                            support_phone = detail.get('spprtPhone')
                            if support_phone:
                                support_phone = support_phone.strip().replace(';', ',')
                            support_phone_hours = detail.get('spprtHours')
                            if support_phone_hours:
                                support_phone_hours = support_phone_hours.strip().replace(';', ',')

                    data = [[
                        name,
                        vendor,
                        website,
                        desc,
                        target_customer,
                        customer_size,
                        licensing_terms,
                        country,
                        support_phone,
                        support_phone_hours,
                        cat,
                        profile,
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
        'Company',
        'Website',
        'Description',
        'Target Customer',
        'Customer Size',
        'Licensing Terms',
        'Country',
        'Phone',
        'Phone Hours',
        'Category',
        'Profile'
    ]])


def main():
    csv_header()
    mod = SaasMax()
    mod.get_data()


def get_data():
    main()
