#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import re
from bs4 import BeautifulSoup
from maxpreps import FootballProfile, FootballMap
from utils import request


def get_state_class(soup):
    final_clas = []
    clas = [a for a in soup.find_all('a', attrs={'href': re.compile(r'/division/')})]
    if clas:
        for c in clas:
            txt = c.get_text().strip()
            # if 'Class ' in txt:
            final_clas.append((txt, 'http://www.maxpreps.com' + c.get('href')))
        return final_clas
    return None


class RowParser:
    def __init__(self, tr_soup):
        self.soup = tr_soup
        self.trs = []

    def get_name(self):
        return self.soup.find('a').get_text().strip()

    def get_rating(self):
        return self.soup.find('td', class_='rating').get_text().strip()

    def get_strength(self):
        return self.soup.find('td', class_='strength').get_text().strip()

    def get_profle_url(self):
        return 'http://www.maxpreps.com' + self.soup.find('a').get('href').strip()

    def get_search_num(self):
        return self.soup.find('td', class_='rank').get_text().strip()


class ProfileParser:
    def __init__(self, s, cookies, profile_soup, search_num, name, rating, strength, url):
        self.s = s
        self.cookies = cookies
        self.num = search_num
        self.name = name
        self.rating = rating
        self.strength = strength
        self.url = url
        self.soup = profile_soup
        self.data = []

    def get_data(self):
        fp = FootballProfile(self.name, self.soup)
        num = self.num
        overall = fp.overall()
        rating = self.rating
        strength = self.strength
        link = self.url
        name = self.name
        state_class_name = fp.state_class_division_name()
        state_class_rank = fp.state_division_rank()
        nat_rank = fp.nat_rank()
        state_rank = fp.state_rank()
        coach = fp.coach()
        street = fp.street()
        city = fp.city()
        state = fp.state()
        zipcode = fp.zipcode()
        home_link = fp.home_link()
        sw = fp.school_website()

        ad = None
        phone = None
        gender = None
        school = None
        addr_link = fp.address_link()
        if addr_link:
            soup = request(self.s, addr_link, self.cookies)
            if soup:
                fm = FootballMap(soup)
                ad = fm.ad()
                phone = fm.phone()
                gender, school = fm.typ()

        data = [[
            num, overall, rating, strength,
            link, name, nat_rank, state_rank,
            coach, street, city, state, zipcode,
            home_link, ad, phone, gender, school, sw,
            state_class_name, state_class_rank
        ]]
        return data
