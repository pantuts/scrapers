#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import csv
import os
import requests
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_tld
from xml.dom import minidom


class TopAlternatives:
    def __init__(self):
        self.csv_fname = self.csv_fname = 'TOPALTERNATIVES_' + \
            datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %I:%M')
        self.sitemap = 'https://topalternatives.com/post-sitemap.xml'
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
            fname = os.path.expanduser('~') + '/.topalternatives-xmlsrc'
            if os.path.exists(fname):
                os.remove(fname)
            with open(fname, 'a+') as f:
                f.write(str(self.soup))

            xmlsrc = minidom.parse(fname)
            locs = xmlsrc.getElementsByTagName('loc')
            final_locs = []
            for loc in locs:
                if loc.lastChild.data == 'https://topalternatives.com':
                    pass
                else:
                    final_locs.append(str(loc.lastChild.data))

            final_locs = list(set(final_locs))
            self.soup = None
            return final_locs

    def get_data(self, url):
        self.request(url)
        if self.soup:
            if self.soup.select('div.tool'):
                data = []
                for div in self.soup.select('div.tool'):
                    name = div.find('h2').get_text().strip()
                    try:
                        website = get_tld(div.find('a').get('href').strip())
                    except:
                        return ''
                    desc = ''
                    for p in div.select('p'):
                        desc += p.get_text().strip() + '\n'
                    desc = desc.strip().replace(';', ',')
                    data.append([name, website, desc])
                    print('[+] Done >> ' + name)
                self.write_csv(data)
                self.soup = None

    def write_csv(self, data):
        for d in data:
            with open(self.csv_fname + '.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([e for e in d])
                f.flush()


if __name__ == '__main__':
    ta = TopAlternatives()
    locs = ta.get_sitemap()
    if locs:
        for loc in locs:
            ta.get_data(loc)
