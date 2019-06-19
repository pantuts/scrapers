#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import csv
import re
import requests
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tld import get_tld


class SoftwareSuggest:
    def __init__(self):
        self.csv_fname = self.csv_fname = 'SOFTWARESUGGEST_' + \
            datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %I:%M')
        self.soup = None
        self.home_url = 'https://www.softwaresuggest.com/home'
        self.ALL_PAGES = 1
        self.CURRENT_PAGE = 1

    def request(self, url, redir=False):
        try:
            agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) '
            agent += 'AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.463.0 Safari/534.3'
            headers = {
                'User-Agent': agent
            }
            if redir:
                try:
                    print('[+] Getting redirect url for: ' + url)
                    req = requests.get(url, headers=headers,
                                       timeout=15, allow_redirects=True)

                    try:
                        ref = req.headers['Refresh']
                        redir_url = re.findall(r'url=(.+\/)$', ref)[0]
                        if redir_url.startswith('https://cmtrack.softwaresuggest.com/'):
                            self.request(redir_url, redir=True)
                    except:
                        ref = req.url
                        redir_url = ref

                    if redir_url.endswith('http://') or redir_url.endswith('https://') or 'softwaresuggest.com' in redir_url:
                        return ''
                    return get_tld(redir_url)
                except:
                    return ''
            else:
                print('[+] Getting source for: ' + url)
                req = requests.get(url, headers=headers, timeout=15)

            soup = BeautifulSoup(req.text, 'html.parser')
            self.soup = soup
            return True
        except Exception as e:
            print('[-] ERROR: >> ' + str(e))
            self.soup = None
            return False

    def get_categories(self):
        self.request(self.home_url)
        if self.soup:
            cats = []
            hrefs = self.soup.select('#category-grid div table tr td a')
            for a in hrefs:
                cats.append('https://www.softwaresuggest.com/' +
                            a.get('href').strip())
            self.soup = None
            return cats
        return False

    def get_profiles(self, cat_url):
        pp = '[+] =========================> PAGE %d' % self.CURRENT_PAGE
        pp += ' <========================='

        profiles = []
        self.request(cat_url)
        if self.soup:

            try:
                a_page = self.soup.find(
                    'li', attrs={'class': 'last'}).find_next().get('href')
                self.ALL_PAGES = int(re.findall('page=(.+)', a_page)[0])
            except:
                self.ALL_PAGES = 1

            if self.CURRENT_PAGE == 1:
                print(pp)

            items = self.soup.select('div.product-item.product-item-holder')
            if items:
                for div in items:
                    rating = 0
                    review_count = 0
                    a = ''
                    _product = div.find(
                        'span', attrs={'itemprop': 'name'}) or ''
                    if not _product:
                        continue
                    if _product:
                        product = _product.get_text().strip()
                    _i = div.select('i.pull-left') or []
                    if _i:
                        i = _i[0].get('class')[0]
                        i = i.replace('s', '')
                        if len(i) > 1:
                            rating = i[:1] + '.' + i[1:]
                        else:
                            rating = i
                        if _i[0].next:
                            if _i[0].next.name == 'span':
                                review_count = _i[0].next.get_text().strip()
                        if rating == '0':
                            review_count = 0
                    _a = div.find('a', text=re.compile('View Profile')) or ''
                    if _a:
                        a = 'https://www.softwaresuggest.com' + \
                            _a.get('href').strip()
                    profile = {
                        'product': product,
                        'rating': rating,
                        'review_count': review_count,
                        'profile_link': a
                    }
                    profiles.append(profile)

        if profiles:
            for p in profiles:
                self.get_profile_data(p)

        if self.CURRENT_PAGE < self.ALL_PAGES:
            self.CURRENT_PAGE = self.CURRENT_PAGE + 1
            pp = '[+] =========================> PAGE %d' % self.CURRENT_PAGE
            pp += ' <========================='

            if 'page' in cat_url:
                c_url = re.findall(
                    '(.+?page=).+$', cat_url)[0] + str(self.CURRENT_PAGE)
            else:
                c_url = cat_url + '?page=%d' % self.CURRENT_PAGE
            print(pp)
            self.get_profiles(c_url)

        self.CURRENT_PAGE = 1
        self.soup = None
        return False

    def get_profile_data(self, p_dict):
        self.request(p_dict['profile_link'])
        if self.soup:
            company = self.get_company()
            website = self.get_website()
            hq = self.get_headquarter()
            desc = self.get_description()
            profile = p_dict['profile_link']

            data = [[
                p_dict['product'],
                company,
                website,
                hq,
                desc,
                p_dict['rating'],
                p_dict['review_count'],
                profile
            ]]
            self.write_csv(data)
            self.soup = None
            print('[+] Done >> ' + p_dict['product'])

    def get_company(self):
        try:
            return self.soup.find('td', text=re.compile('Company Name')).find_next().get_text().strip()
        except:
            return ''

    def get_headquarter(self):
        try:
            return self.soup.find('td', text=re.compile('Headquarter')).find_next().get_text().strip()
        except:
            return ''

    def get_website(self):
        try:
            a_tmp = 'https://www.softwaresuggest.com'
            a = self.soup.find('td', text=re.compile(
                'Website')).find_next('a').get('href').strip()
            if a.startswith('/visitwebsite'):
                a = a_tmp + a
            return self.request(a, redir=True)
        except:
            return ''

    def get_description(self):
        try:
            return self.soup.find('h4').find_next('p').get_text().strip().replace(';', '')
        except:
            return ''

    def write_csv(self, data):
        for d in data:
            with open(self.csv_fname + '.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([e for e in d])
                f.flush()


if __name__ == '__main__':
    done = [i.strip() for i in open('done.txt') if i]
    ss = SoftwareSuggest()
    cats = ss.get_categories()
    if cats:
        for cat_url in cats:
            if cat_url not in done:
                ss.get_profiles(cat_url)
                with open('done.txt', 'a+') as f:
                    f.write(cat_url + '\n')
