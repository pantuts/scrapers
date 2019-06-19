#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import re


class FootballProfile:
    def __init__(self, name, soup):
        self.name = name
        self.soup = soup

    def name(self):
        return self.name

    def nat_rank(self):
        try:
            return self.soup.find('dt', \
                text=re.compile(r'National Rank')).find_next('dd').get_text().strip()
        except:
            return None

    def overall(self):
        try:
            return self.soup.find('dt', \
                text=re.compile(r'Overall')).find_next('dd').get_text().strip()
        except:
            return None

    def state_rank(self):
        try:
            return self.soup.find('dt', \
                text=re.compile(r'State.+Rank?')).find_next('dd').get_text().strip()
        except:
            return None

    def state_class_division_name(self):
        try:
            return self.soup.find('meta', \
                attrs={'name': 'description'}).get('content').rpartition('and')[-1].replace('rankings.', '').strip()
        except:
            return None

    def state_division_rank(self):
        try:
            return self.soup.find('a', \
                attrs={'href': re.compile(r'#state_division_rankings')}).find('span').get_text().strip()
        except:
            try:
                return self.soup.find('a',  \
                    attrs={'href': re.compile(r'#section_division_rankings')}).find('span').get_text().strip()
            except:
                try:
                    return self.soup.find('a',  \
                        attrs={'href': re.compile(r'#section_rankings')}).find('span').get_text().strip()
                except:
                    return None

    def coach(self):
        try:
            return self.soup.find('dt', \
                text=re.compile(r'Coach')).find_next('dd').get_text().replace(';', ',').strip()
        except:
            return None

    def address_link(self):
        try:
            return 'http://www.maxpreps.com' + \
                self.soup.find('address').find_previous('a').get('href').replace(';', ',').strip()
        except:
            return None

    def _address(self, typ):
        try:
            addr = self.soup.find('address').get_text()
            addr = [s.strip() for s in addr.split(',')]
            street = addr[-3]
            city = addr[-2]
            _tmp = addr[-1].split()
            state = _tmp[0]
            zipcode = _tmp[1]
            addr = {
                'street': street,
                'city': city,
                'state': state,
                'zipcode': zipcode
            }
            return addr[typ]
        except:
            return None

    def street(self):
        try:
            return self._address('street').replace(';', ',').strip()
        except:
            return None

    def city(self):
        try:
            return self._address('city').replace(';', ',').strip()
        except:
            return None

    def state(self):
        try:
            return self._address('state').replace(';', ',').strip()
        except:
            return None

    def zipcode(self):
        try:
            return self._address('zipcode').replace(';', ',').strip()
        except:
            return None

    def home_link(self):
        try:
            return 'http://www.maxpreps.com' + self.soup.find('a', \
                attrs={'data-la': 'school-home', 'data-lc': 'Team-Navigation'}).get('href').strip()
        except:
            return None

    def school_website(self):
        try:
            return self.soup.find('a', \
                attrs={'data-la': 'school-website', 'data-lc': 'Team-Navigation'}).get('href').strip()
        except:
            return None


class FootballMap:
    def __init__(self, soup):
        self.soup = soup

    def ad(self):
        try:
            return self.soup.find('dt', \
                text=re.compile(r'AD')).find_next('dd').get_text().strip()
        except:
            return None

    def phone(self):
        try:
            return self.soup.find('dt', \
                text=re.compile(r'Phone')).find_next('dd').get_text().strip()
        except:
            return None

    def typ(self):
        try:
            t = self.soup.find('dt', \
                text=re.compile(r'Type')).find_next('dd').get_text().strip()
            t = t.split('/')
            gender = t[0].strip()
            school = t[1].strip()
            return gender, school
        except:
            return None, None
