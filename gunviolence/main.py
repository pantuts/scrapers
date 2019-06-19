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
from selenium.webdriver.support.ui import WebDriverWait, Select
import calendar
import csv
import re
import subprocess
import time

FROM_YEAR = 2017
TO_YEAR = 2017

FROM_MONTH = 10
TO_MONTH = 10

FROM_DAY = 1
TO_DAY = 3


class GunViolenceArchive:
    def __init__(self):
        self.dates = []
        self.csv_fname = 'GVA.csv'
        self.query_url = 'http://www.gunviolencearchive.org/query'
        self.url = ''
        # self.url = 'http://www.gunviolencearchive.org/query/0b82e545-08a1-4321-88fe-76e4c3e56327/edit'
        self.from_id = ''
        self.to_id = ''
        self.is_ids_set = False
        self.save_id = 'edit-actions-execute'
        self.month_ranges = {}
        self.driver = None
        self.set_driver()
        self.set_month_ranges()

    def set_driver(self):
        self.driver = webdriver.Chrome()
        print('[+] Driver started...')

    def set_month_ranges(self):
        _r = {}
        for i in range(1, 13):
            _r[str(i)] = calendar.monthrange(2017, i)
        self.month_ranges = _r

    def copy_text(self, txt_date):
        subprocess.call('echo %s|xclip -i -r -selection clipboard' %
                        txt_date, shell=True)

    def set_ids(self, soup):
        ids = soup.find_all('input', id=re.compile(
            r'edit-query-filters'), class_='date-picker-single')
        for i in ids:
            if 'date-from' in i.get('id'):
                self.from_id = i.get('id')
            if 'date-to' in i.get('id'):
                self.to_id = i.get('id')
        self.is_ids_set = True

    def add_rule(self):
        try:
            print('[+] Adding rule...')
            self.driver.get(self.query_url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'filter-dropdown-trigger')))

            rule = self.driver.find_element_by_class_name(
                'filter-dropdown-trigger')
            rule.click()
            rule_date = rule.find_element_by_xpath(
                '//*[@id="edit-query-filters-new-dropdown"]/ul/span[1]/li[2]/a')
            time.sleep(1)
            rule_date.click()
            time.sleep(2)

            # any date will do
            self.copy_text('10/1/2017')
            if not self.is_ids_set:
                self.set_ids(BeautifulSoup(self.driver.page_source, 'lxml'))

            fr = self.driver.find_element_by_id(self.from_id)
            to = self.driver.find_element_by_id(self.to_id)
            save = self.driver.find_element_by_id(self.save_id)
            fr.clear()
            fr.click()
            fr.send_keys(Keys.CONTROL + 'v')
            time.sleep(1)
            to.clear()
            to.click()
            to.send_keys(Keys.CONTROL + 'v')
            time.sleep(1)
            save.click()

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'block-system-main')))
            self.url = self.driver.current_url + '/edit'
            print('[+] URL: %s' % self.url)
        except Exception as e:
            print(e)

    def get_data(self):
        current_year = FROM_YEAR
        current_month = FROM_MONTH
        current_day = FROM_DAY

        self.add_rule()
        time.sleep(2)

        looping = True
        while looping:
            day = '%d/%d/%d' % (current_month, current_day, current_year)
            self.copy_text(day)
            print(
                '-------------------------------START: %s-------------------------------' % str(day))

            try:
                self.driver.get(self.url)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'filters-container')))

                if not self.is_ids_set:
                    self.set_ids(BeautifulSoup(
                        self.driver.page_source, 'lxml'))

                fr = self.driver.find_element_by_id(self.from_id)
                to = self.driver.find_element_by_id(self.to_id)
                save = self.driver.find_element_by_id(self.save_id)

                fr.clear()
                fr.click()
                fr.send_keys(Keys.CONTROL + 'v')
                time.sleep(1)
                to.clear()
                to.click()
                to.send_keys(Keys.CONTROL + 'v')
                time.sleep(1)
                save.click()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'block-system-main')))

                page = 1
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
                trs = soup.select('tr.odd, tr.even')
                if trs:
                    self.get_rows(trs, page, day)
                time.sleep(2)

                nxt_page = soup.find('a', {'title': 'Go to next page'})
                while (nxt_page):
                    pager_next = self.driver.find_element_by_class_name(
                        'pager-next')
                    nxt_button = pager_next.find_element_by_tag_name('a')
                    nxt_button.click()

                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'block-system-main')))

                    page = page + 1
                    soup = BeautifulSoup(self.driver.page_source, 'lxml')
                    trs = soup.select('tr.odd, tr.even')
                    if trs:
                        self.get_rows(trs, page, day)
                    nxt_page = soup.find('a', {'title': 'Go to next page'})
                    time.sleep(2)
            except Exception as e:
                print(e)
                current_year = current_year + 1
                current_month = current_month + 1
                current_day = current_day + 1
                continue

            print(
                '-------------------------------END: %s-------------------------------' % str(day))

            if current_day >= TO_DAY and current_month >= TO_MONTH and current_year >= TO_YEAR:
                looping = False
                self.driver.quit()
            elif current_day == self.month_ranges[str(current_month)][1]:
                current_month = current_month + 1
                current_day = 1
            elif current_day == self.month_ranges[str(current_month)][1] and current_month == 12:
                current_year = current_year + 1
                current_month = 1
            else:
                current_day = current_day + 1

    def get_rows(self, trs, page, day):
        print('[+] Page %s' % str(page))

        lrd = self.get_lastrow_date(trs)
        same_date = self.compare_dates(lrd, day)
        if not same_date:
            print('[!] will not save data, dates are not equal to %s' % day)
            return False

        for tr in trs:
            tds = tr.find_all('td')
            if tds and len(tds) == 7:
                dte = tds[0].get_text().strip()
                state = tds[1].get_text().strip()
                city_country = tds[2].get_text().strip()
                address = tds[3].get_text().strip()
                killed = tds[4].get_text().strip()
                injured = tds[5].get_text().strip()
                self.write_csv([[
                    dte, state, city_country, address, killed, injured
                ]])

    def get_lastrow_date(self, trs):
        lastrow_date = None
        for i, tr in enumerate(trs):
            if i == len(trs) - 1:
                tds = tr.find_all('td')
                if tds and len(tds) == 7:
                    lastrow_date = tds[0].get_text().strip()
        return lastrow_date

    def compare_dates(self, d1, d2):
        try:
            return datetime.strptime(d1, '%B %d, %Y') == datetime.strptime(d2, '%m/%d/%Y')
        except Exception as e:
            print(e)
            return False

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
    gva = GunViolenceArchive()
    gva.get_data()
