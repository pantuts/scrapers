#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import csv
import json
import re
import requests
import sys
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_tld


class GrowthVerse:
    def __init__(self):
        self.csv_fname = self.csv_fname = 'GROWTHVERSE_' + \
            datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %I:%M')
        self.url = 'http://www.growthverse.com/api/v2/companies.json?page=%d'
        self.total_pages = 0
        self.current_page = 0

    def request(self, url):
        print('Getting data for: ' + url)
        try:
            agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) '
            agent += 'AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.463.0 Safari/534.3'
            headers = {
                'User-Agent': agent
            }
            req = requests.get(url, headers=headers, timeout=15)
            return req.json()
        except Exception as e:
            print('[-] ERROR: >> ' + str(e))
            return False

    def get_total_pages(self, jsn_entry):
        return jsn_entry.get('meta').get('pagination').get('total_pages')

    def get_current_page(self, jsn_entry):
        return jsn_entry.get('meta').get('pagination').get('current_page')

    def get_description(self, jsn_entry):
        desc = jsn_entry.get('description')
        if desc:
            soup = BeautifulSoup(desc, 'html.parser')
            dsc = soup.get_text() or ''
            return dsc.strip().replace(';', '')
        return ''

    def get_profile_link(self, jsn_entry):
        return jsn_entry.get('url') or ''

    def get_company_name(self, jsn_entry):
        return jsn_entry.get('companyname').strip()

    def get_location(self, jsn_entry):
        return jsn_entry.get('location') or ''

    def get_email(self, jsn_entry):
        return jsn_entry.get('contactemail') or ''

    def get_website(self, jsn_entry):
        if jsn_entry.get('websiteurl'):
            url = jsn_entry.get('websiteurl')
            if url == 'N/A':
                return ''
            if not url.startswith('http'):
                url = 'http://' + url
            return get_tld(url)
        return ''

    def get_year_founded(self, jsn_entry):
        return jsn_entry.get('yearfounded') or ''

    def get_categories(self, jsn_entry):
        if jsn_entry.get('categories'):
            cats = ''
            for cat in jsn_entry.get('categories'):
                cats += cat.get('title').strip() + ', '
            return cats.strip(', ')
        return ''

    def get_fundings(self, jsn_entry):
        amount = 0
        investors = ''
        if jsn_entry.get('funding'):
            amount = jsn_entry.get('funding').get('amount')
            investors = jsn_entry.get('funding').get('investors') or ''
            if amount == 0:
                return amount, investors
            return '$%s Million' % str(amount), investors
        return amount, investors

    def get_employees(self, jsn_entry):
        if jsn_entry.get('social'):
            return jsn_entry.get('social').get('employees') or 0
        return 0

    def get_data(self, url):
        jsn = self.request(url)
        if jsn:
            entries = jsn.get('data')
            if entries:
                for jsn_entry in entries:
                    company_name = self.get_company_name(jsn_entry)
                    website = self.get_website(jsn_entry)
                    desc = self.get_description(jsn_entry)
                    location = self.get_location(jsn_entry)
                    email = self.get_email(jsn_entry)
                    founded = self.get_year_founded(jsn_entry)
                    categories = self.get_categories(jsn_entry)
                    funding_amount, investors = self.get_fundings(jsn_entry)
                    employees = self.get_employees(jsn_entry)
                    profile = self.get_profile_link(jsn_entry)
                    self.write_csv([[
                        company_name,
                        website,
                        location,
                        desc,
                        email,
                        founded,
                        categories,
                        funding_amount,
                        investors,
                        employees,
                        profile
                    ]])
                    print('[+] Done >> ' + company_name)

            self.total_pages = self.get_total_pages(jsn)
            self.current_page = self.get_current_page(jsn)
            if self.total_pages == self.current_page:
                sys.exit(0)

    def write_csv(self, data):
        for d in data:
            with open(self.csv_fname + '.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([e for e in d])
                f.flush()


if __name__ == '__main__':
    gv = GrowthVerse()
    # range 25 is just an estimate for looping json responses
    for i in range(25):
        gv.get_data(gv.url % int(i + 1))
