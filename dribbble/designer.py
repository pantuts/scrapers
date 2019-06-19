#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import re
import requests
from configs import MAIN_URL
from utils import HEADERS


class Designer:
    def __init__(self, soup):
        self.soup = soup

    def get_redirect(self, url):
        try:
            print('[+] HEAD request ...')
            r = requests.head(url, headers=HEADERS)
            return r.headers.get('Location').replace('https://', '').replace('http://', '').replace('www.', '')
        except Exception:
            return None

    def shots(self):
        try:
            return int(self.soup.select('li.shots span.count')[0].get_text())
        except Exception:
            return 0

    def projects(self):
        try:
            return int(self.soup.select('li.projects span.count')[0].get_text())
        except Exception:
            return 0

    def followers(self):
        try:
            return int(self.soup.select('li.followers span.count')[0].get_text().replace(',', ''))
        except Exception:
            return 0

    def likes(self):
        try:
            return int(self.soup.select('li.likes span.count')[0].get_text().replace(',', ''))
        except Exception:
            return None

    def tags(self):
        try:
            return int(self.soup.select('li.tags span.count')[0].get_text().replace(',', ''))
        except Exception:
            return None

    def email(self):
        try:
            s = self.soup.select('div.profile-essentials')[0].get_text().strip()
            return re.findall(r'[\w\.-]+@[\w\.-]+', s)[0].strip()
        except Exception:
            return None

    def website(self):
        try:
            return self.soup.find('a', class_='elsewhere-website').get('data-url').strip()
        except Exception:
            return None

    def instagram(self):
        try:
            ins = self.soup.find('a', class_='elsewhere-instagram').get('href')
            ins = MAIN_URL + ins
            ins = self.get_redirect(ins)
            return ins
        except Exception:
            return None

    def facebook(self):
        try:
            fb = self.soup.find('a', class_='elsewhere-facebook').get('href')
            fb = MAIN_URL + fb
            fb = self.get_redirect(fb)
            return fb
        except Exception:
            return None

    def twitter(self):
        try:
            tw = self.soup.find('a', class_='elsewhere-twitter').get('href')
            tw = MAIN_URL + tw
            tw = self.get_redirect(tw)
            return tw
        except Exception:
            return None

    def linkedin(self):
        try:
            ln = self.soup.find('a', class_='elsewhere-linkedin').get('href')
            ln = MAIN_URL + ln
            ln = self.get_redirect(ln)
            return ln
        except Exception:
            return None

    def vimeo(self):
        try:
            vm = self.soup.find('a', class_='elsewhere-vimeo').get('href')
            vm = MAIN_URL + vm
            vm = self.get_redirect(vm)
            return vm
        except Exception:
            return None
