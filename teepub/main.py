#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import csv
import sys
import time


class TeePublic:
    def __init__(self, tags):
        self.tags = tags
        self.csv_fname = 'TEEPUBLIC' + '_' + \
            datetime.fromtimestamp(time.time()).strftime(
                '%Y-%m-%d_%I-%M') + '.csv'
        self.query_url = 'https://www.teepublic.com/t-shirts?query={}'
        self.shirts = []

    def get_shirts(self, soup):
        self.shirts.extend(['https://www.teepublic.com' + a.get('href')
                            for a in soup.select('div.search-designs div.design a.preview')])

    def get_data(self):
        driver = webdriver.Firefox()

        for tag in self.tags:
            print('---------------------------> START: {}'.format(tag))
            new_tag = tag.lower().replace(' ', '-')
            print('[+] Requesting source... {}'.format(self.query_url.format(new_tag)))
            driver.get(self.query_url.format(new_tag))
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'commit')))

            soup = BeautifulSoup(driver.page_source, 'lxml')
            self.get_shirts(soup)

            pagination = True
            while pagination:
                try:
                    driver.find_element_by_class_name('next').click()
                    print('[+] Requesting source... {}'.format(driver.current_url))
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.NAME, 'commit')))
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    self.get_shirts(soup)
                except:
                    pagination = False

            shirts = list(set(self.shirts))
            for s in shirts:
                data = [[s, tag]]
                self.write_csv(data)
            print('--------------------------->END: {}'.format(tag))
            self.shirts = []

    def write_csv(self, data):
        try:
            with open(self.csv_fname, 'a') as f:
                writer = csv.writer(f)
                for d in data:
                    writer.writerow([e for e in d])
                    f.flush()
        except Exception as e:
            print('[-] CSV ERROR: {}'.format(e))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('List of tags needed!')
        sys.exit()

    tags = [t.strip() for t in open(sys.argv[1]) if t.strip()]
    tp = TeePublic(tags)
    tp.get_data()
