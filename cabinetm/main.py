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
from xml.dom import minidom


class Cabinetm:
    def __init__(self):
        self.csv_fname = self.csv_fname = 'CABINETM_' + \
            datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %I:%M')
        self.sitemap = 'https://www.cabinetm.com/sitemap.xml'
        self.soup = None

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

    def get_sitemap(self):
        if self.request(self.sitemap):
            fname = './cabinetm-xmlsrc'
            if os.path.exists(fname):
                os.remove(fname)
            with open(fname, 'a+') as f:
                f.write(str(self.soup))

            xmlsrc = minidom.parse(fname)
            locs = xmlsrc.getElementsByTagName('loc')
            final_locs = []
            for loc in locs:
                d = loc.lastChild.data
                if d.startswith('https://www.cabinetm.com/company/'):
                    final_locs.append(str(d))

            # final_locs = list(set(final_locs))
            self.soup = None
            return final_locs

    def get_data(self, url):
        self.request(url)
        if self.soup:
            if '404 Company Not Found' in str(self.soup):
                return False
            name = self.get_name()
            website = self.get_website()
            hq = self.get_hq()
            description = self.get_desc()
            founded = self.get_founded()

            data = [[name, website, hq, description, founded]]
            self.write_csv(data)
            self.soup = None
            print('[+] Done >> ' + name)

    def get_name(self):
        try:
            return self.soup.find('h2').get_text().strip().replace(';', ',')
        except:
            return ''

    def get_hq(self):
        try:
            return self.soup.find('label', text=re.compile('Headquarters')).find_next('div').get_text().strip().replace(';', ',')
        except:
            return ''

    def get_website(self):
        try:
            s = self.soup.find(
                'a', attrs={'id': 'companyUrlLink'}).get('href').strip()
            if not s.startswith('http'):
                s = 'http://' + s
            return get_tld(s)
        except:
            return ''

    def get_desc(self):
        try:
            return self.soup.find('div', attrs={'class': 'description'}).get_text().strip().replace('Description\n', '').strip().replace(';', ',')
        except:
            return ''

    def get_founded(self):
        try:
            return self.soup.find('label', text=re.compile('Founded')).find_next('div').get_text().strip()
        except:
            return ''

    def write_csv(self, data):
        for d in data:
            with open(self.csv_fname + '.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([e for e in d])
                f.flush()


if __name__ == '__main__':
    cab = Cabinetm()
    locs = cab.get_sitemap()
    if locs:
        for loc in locs:
            cab.get_data(loc)
