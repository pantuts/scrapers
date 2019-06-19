#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts
# dependencies: selenium, phantomjs, beautifulsoup (with lxml or use html.parser instead of lxml)

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import re
from bs4 import BeautifulSoup
from selenium import webdriver

URL = 'http://www.oklahomacounty.org/assessor/Searches/AN-R_HistoricalView.asp?Accountno=R120682380'


def get_page_source(url):
    try:
        print('[+] Getting source: %s' % url)
        driver = webdriver.PhantomJS(service_args=['--disk-cache=true'])
        driver.get(url)
        return driver.page_source
    except:
        return None


class OKCParser(object):
    def __init__(self, soup):
        self.soup = soup

    def get_account(self):
        try:
            return self.soup.find('font', text=re.compile(r'Account #')).find_next('font').get_text().strip()
        except:
            return None

    def get_lot_width(self):
        try:
            return self.soup.find('font', text=re.compile(r'Lot Width')).find_next('font').get_text().strip()
        except:
            return None

    def get_depth(self):
        try:
            return self.soup.find('font', text=re.compile(r'Depth')).find_next('font').get_text().strip()
        except:
            return None


if __name__ == '__main__':
    src = get_page_source(URL)
    if src:
        soup = BeautifulSoup(src, 'lxml')
        okc = OKCParser(soup)
        acc = okc.get_account()
        lot = okc.get_lot_width()
        dep = okc.get_depth()
        print('Account: ' + str(acc))
        print('Lot Width: ' + str(lot))
        print('Depth: ' + str(dep))
