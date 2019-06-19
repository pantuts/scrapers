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

XML_SRC = 'http://technologyadvice.com/sitemap.xml'


class TechnologyAdvice:
    def __init__(self):
        self.csv_fname = self.csv_fname = 'TechnologyAdvice_' + \
            datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %I:%M')
        self.soup = None
        self.product_url = None

    def request(self, url, sitemap=False):
        if not sitemap:
            print('[+] Getting source for: ' + url)
        else:
            print('[+] Getting sitemap data: ' + url)
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) \
                AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.463.0 Safari/534.3'
            }
            req = requests.get(url, headers=headers, timeout=15)
            if not sitemap:
                soup = BeautifulSoup(req.text, 'html.parser')
                self.soup = soup
                self.product_url = url
            else:
                return req.text
        except Exception as e:
            print('[-] ERROR: >> ' + str(e))
            return False

    def get_xml_products(self):
        ALL_PRODUCTS = []
        mainxml = self.request(XML_SRC, sitemap=True)
        if mainxml:
            # http://technologyadvice.com/sitemap-pt-products-2015-10.xml
            products_xml = re.findall(r'http://.+?products-.+\.xml', mainxml)
            if products_xml:
                for px in products_xml:
                    pxml = self.request(px, sitemap=True)
                    if pxml:
                        # http://technologyadvice.com/products/servicetrade-reviews/
                        prods = re.findall(r'(http://.+?products.+\/)<', pxml)
                        ALL_PRODUCTS.extend(prods)
                return list(set(ALL_PRODUCTS))
        return False

    def get_data(self):
        title = self.get_product_title()
        features = self.get_features()
        review = self.get_review_count()
        rating = self.get_rating()
        desc = self.get_description()
        tech_advisor = self.get_tech_advisor()

        data = [[title, features, review, rating,
                 desc, tech_advisor, self.product_url]]
        self.write_csv(data)
        print('[+] Done: ' + title)

        self.soup = None
        self.product_url = None

    def get_product_title(self):
        try:
            return self.soup.find('h1', attrs={'class': 'product-title'}).get_text().strip()
        except:
            return 'ProductDefaultName'

    def get_features(self):
        features = []
        try:
            for div in self.soup.select('.product-terms ul div.attribute-term'):
                for a in div.select('a'):
                    features.append(a.get_text().strip())
            return '\n'.join(features)
        except:
            return ''

    def get_review_count(self):
        try:
            count = self.soup.find(
                'span', attrs={'itemprop': 'reviewCount'}).get_text().strip()
            count = int(count.replace('(', '').replace(' reviews)', ''))
            return count
        except:
            return 0

    def get_rating(self):
        try:
            return float(self.soup.find('div', attrs={'id': 'reviews_stars'}).get('content'))
        except:
            return 0

    def get_description(self):
        try:
            desc = self.soup.find('div', attrs={
                                  'id': 'about-product-header'}).get_text().replace('\nScreenshots', '').strip()
            desc = desc.replace(';', ',')
            return desc
        except:
            return ''

    def get_tech_advisor(self):
        advisor = ''
        phone = ''
        try:
            author = self.soup.find(
                'p', attrs={'class': 'author-link author'}).get_text().strip()
            if author:
                try:
                    phone = self.soup.find(
                        'p', attrs={'class': 'author-phone'}).get_text().strip()
                except:
                    phone = ''
                advisor += author + '\n'
                advisor += phone.replace(';', ',')
                return advisor.strip()
        except:
            return ''

    def write_csv(self, data):
        for d in data:
            with open(self.csv_fname + '.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([e for e in d])
                f.flush()


if __name__ == '__main__':
    ta = TechnologyAdvice()
    prods = ta.get_xml_products()
    if prods:
        with open('products.txt', 'a') as f:
            for prod in prods:
                f.write(prod + '\n')
        for prod in prods:
            ta.request(prod)
            if ta.soup:
                ta.get_data()

    # to be used for rerunning
    # ta = TechnologyAdvice()
    # if os.path.exists('products.txt'):
    #     prods = [i.strip() for i in open('products.txt').readlines() if i.strip()]
    # else:
    #     prods = ta.get_xml_products()
    # if prods:
    #     if not os.path.exists('products.txt'):
    #         with open('products.txt', 'a') as f:
    #             for prod in prods:
    #                 f.write(prod + '\n')
    #     for prod in prods:
    #         ta.request(prod)
    #         if ta.soup:
    #             ta.get_data()
