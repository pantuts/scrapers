#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import os
import re
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_fld
from utils import setup_logger, request, CSVUtils

logger = setup_logger(__name__)
csv_utils = CSVUtils()

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0].title()
NAME = 'Techpoint'
CSV_FNAME = NAME + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.csv'

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')

BROWSE_URL = 'http://techpoint.org/tech-directory/'


class Techpoint:
    def get_profiles(self):
        resp = request(BROWSE_URL)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            return [a.get('href') for a in soup.select('h2.cTitle a')]

    def get_data(self, url):
        resp = request(url)
        if resp:
            soup = BeautifulSoup(resp.text, 'lxml')
            name = self.get_name(soup)
            if not name:
                return False
            site = self.get_website(soup)
            desc = self.get_desc(soup)
            hq = self.get_hq(soup)
            cats = self.get_cats(soup)
            founded = self.get_founded(soup)
            fb, tw, ln, gp = self.get_socials(soup)
            email = self.get_email(soup)
            phone = self.get_phone(soup)
            data = [[
                name,
                site,
                desc,
                hq,
                founded,
                email,
                phone,
                fb,
                tw,
                ln,
                gp,
                cats,
                url
            ]]
            write_data(data, name)

    def get_name(self, soup):
        try:
            return soup.find('h1', class_='companyName').get_text().strip()
        except Exception:
            return None

    def get_desc(self, soup):
        try:
            return soup.find('div', \
                class_='description').get_text().replace('DESCRIPTION:', '').strip()
        except Exception:
            return None

    def get_cats(self, soup):
        try:
            return ', '.join([a.get_text().strip() for a in soup.find('div', \
                class_='categories').find_all('a')])
        except Exception:
            return None

    def get_founded(self, soup):
        try:
            return soup.find('div', \
                class_='founded').get_text().replace('FOUNDED: ', '').strip()
        except Exception:
            return None

    def get_socials(self, soup):
        try:
            sc = [a.get('href') for a in soup.select('span.social-links a')]
            fb = None
            tw = None
            ln = None
            gp = None
            for s in sc:
                if 'facebook.com' in s:
                    fb = s
                elif 'twitter' in s:
                    tw = s
                elif 'linkedin' in s:
                    ln = s
                elif 'plus.google' in s:
                    gp = s
            return fb, tw, ln, gp
        except Exception:
            return None, None, None, None

    def get_website(self, soup):
        try:
            s = soup.find('a', class_='website').get('href')
            if not s.startswith('http'):
                s = 'http://' + s
            return get_fld(s)
        except Exception:
            try:
                s = soup.find('span', text=re.compile(r'WEBSITE')).find_next('span', class_='content').get_text().strip()
                if not s.startswith('http'):
                    s = 'http://' + s
                return get_fld(s)
            except Exception:
                return None

    def get_email(self, soup):
        try:
            return soup.find('span', \
                text=re.compile(r'EMAIL')).find_next('span', class_='content').get_text().strip()
        except Exception:
            return None

    def get_phone(self, soup):
        try:
            return soup.find('span', \
                text=re.compile(r'PHONE')).find_next('span', class_='content').get_text().strip()
        except Exception:
            return None

    def get_hq(self, soup):
        try:
            return soup.find('span', text=re.compile(r'ADDRESS')).find_next('span', class_='content').get_text().strip()
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
        'Website',
        'Description',
        'HQ',
        'Founded',
        'Email',
        'Phone',
        'Facebook',
        'Twitter',
        'Linkedin',
        'GooglePlus',
        'Categories',
        'Profile'
    ]])


def main():
    csv_header()
    mod = Techpoint()
    profiles = mod.get_profiles()
    for profile in profiles:
        mod.get_data(profile)


def get_data():
    main()
