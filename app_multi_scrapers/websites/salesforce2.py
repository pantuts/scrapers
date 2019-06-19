#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import os
import random
import re
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup
from datetime import datetime
from utils import setup_logger, request, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'Salesforce'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

APPS_URL = 'https://appexchange.salesforce.com/results?pageNo={}'
APPS_AJAX_URL = 'https://appexchange.salesforce.com/appxstore'


class SalesforceApp:
    def __init__(self, page):
        self.page = int(page)
        self.apps_done = []
        self.SHOW_MORE_ID = 'appx-load-more-button-id'

    def get_links(self, soup):
        return [a.get('href') for a in soup.select('div#j_id0:AppxLayout:listings a.appx-tile.appx-tile-app.tile-link-click')]

    def driver_wait(self, driver):
        waiting = True
        while waiting:
            time.sleep(1)
            try:
                show_more = driver.find_element_by_id(self.SHOW_MORE_ID)
                if show_more.is_enabled():
                    waiting = False
            except Exception:
                pass

    def get_profiles(self):
        profiles = []
        total_apps = 0

        driver = webdriver.Chrome()
        driver.get(APPS_AJAX_URL)
        # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, self.SHOW_MORE_ID)))
        # self.driver_wait(driver)

        logger.info('WebDriver - Show More - Page 1.')

        soup = BeautifulSoup(driver.page_source, 'lxml')
        pf = self.get_links(soup)
        profiles = pf
        if self.page == 1:
            for profile in profiles:
                self.get_data(profile)
            logger.info('Profiles count: {}'.format(len(self.apps_done)))
        else:
            self.apps_done.extend(profiles)
        total_apps = int(soup.find('span', id='total-items-store').get_text().strip())

        err_count = 0
        page = 1
        pagination = True
        while pagination:
            show_more = None
            try:
                show_more = driver.find_element_by_id(self.SHOW_MORE_ID)
            except Exception:
                pagination = False

            if self.page > page:
                if show_more:
                    try:
                        page = page + 1
                        logger.info('WebDriver - Show More - Page {}.'.format(page))
                        show_more.click()
                        # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, self.SHOW_MORE_ID)))
                        # self.driver_wait(driver)

                        soup = BeautifulSoup(driver.page_source, 'lxml')
                        pf = list(filter(lambda x: x not in self.apps_done, self.get_links(soup)))
                        self.apps_done.extend(pf)
                    except Exception:
                        pass
            else:
                if show_more:
                    try:
                        page = page + 1
                        logger.info('WebDriver - Show More - Page {}.'.format(page))
                        show_more.click()
                        # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, self.SHOW_MORE_ID)))
                        # self.driver_wait(driver)
                    except Exception:
                        # err_count = err_count + 1
                        pass

                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    pf = list(filter(lambda x: x not in self.apps_done, self.get_links(soup)))
                    profiles = pf
                else:
                    logger.info('WebDriver - Show More finished!')
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    pf = list(filter(lambda x: x not in self.apps_done, self.get_links(soup)))
                    profiles = pf
                    # pagination = False
                    # err_count = err_count + 1

                for profile in profiles:
                    self.get_data(profile)
                logger.info('Profiles count: {}'.format(len(self.apps_done)))

            slp = random.randint(2, 10)
            logger.info('WebDriver - reloading in {} seconds.'.format(slp))
            for i in range(1, slp + 1):
                sys.stdout.write('Loading in: {}\r\r'.format(i))
                sys.stdout.flush()
                time.sleep(1)

            if len(self.apps_done) == total_apps:
                pagination = False
        driver.quit()

    def get_data(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            if not name:
                return False
            desc = self.get_description(soup)
            rating = self.get_rating(soup)
            reviews = self.get_reviews(soup)
            listed = self.get_listed_on(soup)
            latest = self.get_latest_release(soup)
            cat = self.get_categories(soup)

            data = [[
                name,
                desc,
                rating,
                reviews,
                listed,
                latest,
                cat,
                url
            ]]
            write_data(data, name)
            self.apps_done.append(url)

    def get_name(self, soup):
        try:
            return soup.find('p', class_='appx-page-header-root').get_text().strip()
        except Exception:
            return None

    def get_description(self, soup):
        try:
            return soup.find('div', class_='appx-detail-section-description').get_text().strip()
        except Exception:
            return None

    def get_rating(self, soup):
        try:
            r = soup.find('span', class_=re.compile(r'appx-rating-stars-[0-9]')).get('class')[-1].split('-')[-1]
            rating = r[0] if r[-1] == '0' else r[0] + '.' + r[-1]
            if rating in ['0.0', '0.', '0']:
                rating = None
            return rating
        except Exception:
            return None

    def get_reviews(self, soup):
        try:
            r = soup.find('span', class_='appx-rating-amount').get_text().strip()
            return re.sub('\(|\)', '', r)
        except Exception:
            return None

    def get_listed_on(self, soup):
        try:
            return soup.find('div', class_='appx-detail-section-first-listed').find_all('p')[-1].get_text().strip()
        except Exception:
            return None

    def get_latest_release(self, soup):
        try:
            return soup.find('div', class_='appx-detail-section-first-listed').find_all('p')[-1].get_text().strip()
        except Exception:
            return None

    def get_pricing(self, soup):
        try:
            return soup.find('p', class_='appx-pricing-detail-header').get_text().strip()
        except Exception:
            return None

    def get_categories(self, soup):
        try:
            return ', '.join([a.get_text().strip() for a in soup.find('div', class_='appx-headline-details-categories').find_all('a')])
        except Exception:
            return None


def write_data(data, name=None):
    done = csv_utils.write_csv(CSV_FNAME, data, NOW)
    if name:
        if done:
            logger.info(f'[CSV] Done >> {name}')


def csv_header():
    write_data([[
        'Name',
        'Description',
        'Rating',
        'Reviews',
        'Listed On',
        'Latest Release',
        'Category',
        'Profile'
    ]])


def main(page):
    csv_header()
    mod = SalesforceApp(page)
    mod.get_profiles()


def get_data(page=1):
    main(page)
