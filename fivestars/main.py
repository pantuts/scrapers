#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

from configs import STATES, FIVESTARS_BUSINESS_GROUP_OFFSET_API, CSV_FILTERS
from fivestars import FiveStars
from utils import write_csv, generate_filename, request
import csv
import os
import sys


def csv_uniq(csv_fname):
    rows = []
    with open(csv_fname) as csvf:
        reader = csv.reader(csvf)
        for row in reader:
            rows.append(row)
    final_ids = []
    _tmp = []
    # row[12] is 5star profile url
    ids = [row[12] for row in rows]
    for i, idd, in enumerate(ids):
        if idd.strip() not in _tmp:
            final_ids.append(i)
            _tmp.append(idd)
    final_rows = [rows[i] for i in final_ids]
    final_rows.sort()
    write_csv(os.path.basename(csv_fname), final_rows, 'output_uniq')


def biz():
    csv_fname = generate_filename('ALL_BUSINESSES') + '.csv'
    limit = 20
    offset = 0
    pagination = True
    nxt_url = None

    while pagination:
        print('---------------------------------START: BUSINESS API GET: OFFSET {}'.format(offset))
        api_url = FIVESTARS_BUSINESS_GROUP_OFFSET_API.format(limit, offset) if not nxt_url else nxt_url
        resp = request(api_url)
        if resp:
            jsn = resp.json()

            nxt_url = jsn.get('meta').get('next')
            if not nxt_url:
                pagination = False

            data = jsn.get('data')
            if data:
                for biz_group in data:
                    total_biz = biz_group.get('total_businesses')
                    bizs = biz_group.get('businesses')
                    # print('bizs', bizs)
                    if bizs:
                        fstars = FiveStars(bizs)
                        businesses = fstars.get_businesses()
                        for biz in businesses:
                            name = biz.get('name')

                            addr = biz.get('address')
                            street = addr.get('street')
                            city = addr.get('city')
                            state = addr.get('state')
                            zipcode = addr.get('postal_code')

                            phone = biz.get('phone')
                            if phone and len(phone) == 10:
                                phone = '(' + phone[:3] + ') ' + phone[4:]

                            total_locs = total_biz
                            website = biz.get('website')
                            fb = biz.get('facebook')
                            instagram = biz.get('instagram')
                            tw = biz.get('twitter')
                            yelp = biz.get('yelp')
                            prof = biz.get('profile')

                            desc = biz.get('description')
                            hours = biz.get('hours')
                            keywords = biz.get('keywords')
                            logo = biz.get('logo')
                            gplus = biz.get('google_plus')
                            cat = biz.get('category')
                            write_csv(csv_fname, [[
                                name,
                                street,
                                city,
                                state,
                                zipcode,
                                phone,
                                total_locs,
                                website,
                                fb,
                                instagram,
                                tw,
                                yelp,
                                prof,
                                desc,
                                hours,
                                keywords,
                                logo,
                                gplus,
                                cat
                            ]], 'output')
                            print('[+] Done >> {}'.format(name))
        offset += limit
        print('---------------------------------END: BUSINESS API GET: OFFSET {}'.format(offset))


def biz_filter(filters, state):
    csv_fname = state.upper() + '.csv'
    state_abbr = STATES.get(state)
    state_row = CSV_FILTERS.get('state')
    if state_abbr:
        rows = []
        with open('output_uniq/ALL_BUSINESSES.csv') as csvf:
            reader = csv.reader(csvf)
            next(reader, None)
            for row in reader:
                if row[state_row].lower() == state_abbr.lower():
                    new_row = []
                    for flter in filters:
                        filter_row = CSV_FILTERS.get(flter)
                        new_row.append(row[filter_row])
                    rows.append(new_row)
        write_csv(csv_fname, rows, 'output_uniq')


if __name__ == '__main__':
    def help():
        help = '''
        \rUsage: main.py filter|biz|uniq
        \rfilter
            required: columns, state
            columns:
                name
                street
                city
                state
                zipcode
                phone
                total_locs
                website
                fb
                instagram
                tw
                yelp
                prof
                desc
                hours
                keywords
                logo
                gplus
                cat
            state: california, georgia, etc.
            example: main.py filter "name, address, phone, website" california
        \rbiz
            no requirements
            example: main.py biz
        \runiq
            required: csv file
            example: main.py uniq CSV_FILE.csv
        '''
        print(help)
    if len(sys.argv) == 1:
        help()
        exit(0)

    command = sys.argv[1]
    if command == 'filter':
        filters = sys.argv[2]
        filters = filters.split(',')
        state = sys.argv[3]
        biz_filter(filters, state)
    elif command == 'uniq':
        csv_fname = sys.argv[2]
        csv_uniq(csv_fname)
    elif command == 'biz':
        biz()
