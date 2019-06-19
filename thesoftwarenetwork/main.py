#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import csv
import os
import re
import requests
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_tld


class TheSoftwareNetwork:
    def __init__(self):
        self.csv_fname = self.csv_fname = 'THESOFTWARENETWORK_' + \
            datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %I:%M')
        self.soup = None
        self.categories = []
        self.products = []

    def request(self, url):
        print('[+] Getting source for: ' + url)
        try:
            agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) '
            agent += 'AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.463.0 Safari/534.3'
            headers = {
                'User-Agent': agent
            }
            req = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(req.text, 'html.parser')
            self.soup = soup
            return True
        except Exception as e:
            print('[-] ERROR: >> ' + str(e))
            self.soup = None
            return False

    def get_categories(self):
        tmp_cats = self.soup.select('a.normalText')[1:-2]
        if tmp_cats:
            for a in tmp_cats:
                self.categories.append(
                    'http://www.thesoftwarenetwork.com' + a.get('href'))
        self.soup = None

    def get_products_cat(self):
        tmp_prod = self.soup.find_all(
            'a', attrs={'href': re.compile('/Software-Vendors/')})
        if tmp_prod:
            for a in tmp_prod:
                href = a.get('href')
                if href.endswith('/'):
                    href = href + 'Solutions.htm'
                self.products.append(
                    'http://www.thesoftwarenetwork.com' + href)
        self.soup = None

    def get_name(self):
        try:
            return self.soup.find('span', attrs={'class': 'title'}).next.get_text().strip()
        except:
            return ''

    def get_website(self):
        try:
            s = self.soup.find(
                'span', attrs={'class': 'title'}).next.get('href').strip()
            return get_tld(s)
        except:
            return ''

    def get_hq(self):
        try:
            s = self.soup.find(
                'span', attrs={'class': 'title'}).next.next.next.next.next.next.strip()
            return s.replace(';', ',')
        except:
            return ''

    def get_phone(self):
        try:
            s = self.soup.find('span', attrs={
                               'class': 'title'}).next.next.next.next.next.next.next.get_text().strip()
            if s.startswith('http'):
                return ''
            return s[:s.index('http')]
        except:
            return ''

    def get_email(self):
        try:
            s = self.soup.find(
                'a', attrs={'href': re.compile('mailto')}).get('href').strip()
            return s.replace('mailto:', '')
        except:
            return ''

    def get_description(self):
        try:
            tmp_s = self.soup.select('#Table9 td')
            if tmp_s:
                s = tmp_s[2].get_text().strip().replace(';', ',')
                if s:
                    return s
                else:
                    tmp_ss = self.soup.find_all(
                        'span', attrs={'class', 'normalText'})
                    if tmp_ss:
                        ss = tmp_ss[-1].get_text().strip().replace(';', '')
                        return ss
        except:
            return ''

    def get_data(self, prod_url):
        name = self.get_name()
        website = self.get_website()
        hq = self.get_hq()
        contact = self.get_phone()
        email = self.get_email()
        desc = self.get_description()
        profile = prod_url
        data = [[
            name,
            website,
            hq,
            contact,
            email,
            desc,
            profile
        ]]
        self.write_csv(data)
        self.soup = None
        print('[+] Done >> ' + name)

    def write_csv(self, data):
        for d in data:
            with open(self.csv_fname + '.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([e for e in d])
                f.flush()


if __name__ == '__main__':
    CAT_URL = 'http://www.thesoftwarenetwork.com/Business-Software/Default.htm'
    tsn = TheSoftwareNetwork()
    req = tsn.request(CAT_URL)
    if req and tsn.soup:
        tsn.get_categories()
        if tsn.categories:
            for cat in tsn.categories:
                req_cat = tsn.request(cat)
                if req_cat and tsn.soup:
                    tsn.get_products_cat()
        if tsn.products:
            products = list(set(tsn.products))
            for prod in products:
                req_prod = tsn.request(prod)
                if req_prod and tsn.soup:
                    tsn.get_data(prod)
