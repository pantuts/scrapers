#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import csv
import re
import requests
import sys
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_tld
from xml.dom import minidom


class VBProfiles:
    def __init__(self, sitemap):
        self.csv_fname = self.csv_fname = 'VBPROFILES_' + \
            datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %I:%M')
        self.sitemap = sitemap
        self.soup = None

    def request(self, url):
        print('[+] Getting source for: ' + url)
        try:
            agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) '
            agent += 'AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.463.0 Safari/534.3'
            headers = {
                'User-Agent': agent
            }
            req = requests.get(url, headers=headers,
                               allow_redirects=True, timeout=15)
            soup = BeautifulSoup(req.text, 'html.parser')
            self.soup = soup
            return True
        except Exception as e:
            print('[-] ERROR: >> ' + str(e))
            self.soup = None
            return False

    def get_sitemap_locs(self):
        # with open(fname, 'a+') as f:
        #     f.write(str(self.soup))

        xmlsrc = minidom.parse(self.sitemap)
        locs = xmlsrc.getElementsByTagName('loc')
        final_locs = []
        for loc in locs:
            d = loc.lastChild.data
            if d.startswith('http://www.spokeintel.com/companies/'):
                final_locs.append(str(d))

        # final_locs = list(set(final_locs))
        self.soup = None
        return final_locs

    def get_data(self, url):
        self.request(url)
        if self.soup:
            name = self.get_name()
            if not name:
                return False
            website = self.get_website()
            email = self.get_email()
            phone = self.get_telephone()
            hq = self.get_hq()
            description = self.get_desc()
            total_funding = self.get_total_funding()
            founded = self.get_founded()
            alias = self.get_alias()
            industry = self.get_industry()
            employees = self.get_employees()
            profile = url

            data = [[
                name,
                website,
                email,
                phone,
                hq,
                description,
                total_funding,
                founded,
                alias,
                industry,
                employees,
                profile
            ]]
            self.write_csv(data)
            self.soup = None
            print('[+] Done >> ' + name)

    def get_name(self):
        try:
            return self.soup.find('h1').get('title').strip().replace(';', ',')
        except:
            return ''

    def get_hq(self):
        try:
            return self. soup.find('address').get_text().replace('Headquarters', '').replace(';', '').strip()
        except:
            return ''

    def get_website(self):
        try:
            s = self.soup.find('a', attrs={'itemprop': 'url'}).get(
                'href').strip().replace(';', '')
            if not s.startswith('http'):
                s = 'http://' + s
            return get_tld(s)
        except:
            return ''

    def get_desc(self):
        try:
            return self.soup.find('div', attrs={'itemprop': 'articleBody'}).get_text().strip().replace(';', ',')
        except:
            return ''

    def get_founded(self):
        try:
            return self.soup.find('h4', text=re.compile('Founded on')).find_next('span').get_text().strip()
        except:
            return ''

    def get_alias(self):
        try:
            return self.soup.find('h4', text=re.compile('Alias')).find_next('span').get_text().strip().replace(';', '')
        except:
            return ''

    def get_industry(self):
        try:
            return self.soup.find('h4', text=re.compile('Industry')).find_next('span').get_text().strip().replace(';', '')
        except:
            return ''

    def get_employees(self):
        try:
            cards = self.soup.select('div.info-card-value')
            if len(cards) == 4:
                return cards[0].get_text().strip()
            return 'N/A'
        except:
            return 'N/A'

    def get_total_funding(self):
        try:
            cards = self.soup.select('div.info-card-value')
            if len(cards) == 4:
                return cards[2].get_text().strip()
            return 'N/A'
        except:
            return 'N/A'

    def get_telephone(self):
        try:
            return self.soup.find('span', attrs={'itemprop': 'telephone'}).get_text().strip().replace(';', '')
        except:
            return ''

    def get_email(self):
        try:
            return self.soup.find('a', attrs={'itemprop': 'email'}).get_text().strip().replace(';', '')
        except:
            return ''

    def write_csv(self, data):
        for d in data:
            with open(self.csv_fname + '.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([e for e in d])
                f.flush()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python vbp.py sitemap')
        sys.exit(0)
    vbp = VBProfiles(sys.argv[1])
    locs = vbp.get_sitemap_locs()
    if locs:
        for loc in locs:
            vbp.get_data(loc)
