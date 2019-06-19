#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

from configs import FIVESTARS_API
from utils import request


class FiveStars:
    def __init__(self, biz_list):
        self.biz_list = biz_list
        self.biz = None

    def get_businesses(self):
        data = []
        for biz in self.biz_list:
            self.biz = biz
            name = self.name()
            website = self.website()
            addr = self.address()
            desc = self.description()
            hours = self.hours()
            phone = self.phone()
            keywords = self.keywords()
            prof = self.profile()
            logo = self.logo()
            fb = self.fb()
            gplus = self.gplus()
            instagram = self.instagram()
            tw = self.twitter()
            yelp = self.yelp()
            biztype = self.business_type()
            cat = self.category()
            data.append({
                'name': name,
                'website': website,
                'address': addr,
                'description': desc,
                'hours': hours,
                'phone': phone,
                'keywords': keywords,
                'profile': prof,
                'logo': logo,
                'facebook': fb,
                'google_plus': gplus,
                'instagram': instagram,
                'twitter': tw,
                'yelp': yelp,
                'business_type': biztype,
                'category': cat
            })
        return data

    def name(self):
        return self.clean(self.biz.get('name'))

    def website(self):
        return self.biz.get('business_url')

    def address(self):
        addr = self.clean(self.biz.get('address_line1'))
        city = self.clean(self.biz.get('city'))
        postal = self.clean(self.biz.get('postal_code'))
        state = self.clean(self.biz.get('state'))
        state_postal = ' '.join(list(filter(None, [state, postal])))
        address = ', '.join(list(filter(None, [addr, city, state_postal])))
        # return address
        return {
            'street': addr,
            'city': city,
            'postal_code': postal,
            'state': state
        }

    def description(self):
        return self.clean(self.biz.get('description'))

    def phone(self):
        return self.biz.get('phone')

    def total_businesses(self):
        return self.biz.get('total_businesses')

    def keywords(self):
        return self.clean(self.biz.get('keywords'))

    def hours(self):
        return self.clean(self.biz.get('hours'))

    def profile(self):
        return 'https://www.fivestars.com' + self.biz.get('url')

    def fb(self):
        return self.biz.get('facebook_page_url')

    def gplus(self):
        return self.biz.get('google_plus_url')

    def instagram(self):
        return self.biz.get('instagram_url')

    def twitter(self):
        return self.biz.get('twitter_url')

    def yelp(self):
        return self.biz.get('yelp_url')

    def business_type(self):
        try:
            return self.clean(self.biz.get('business_type').get('name'))
        except:
            return None

    def category(self):
        try:
            return self.clean(self.biz.get('business_category').get('name'))
        except:
            return None

    def logo(self):
        return self.biz.get('logo')

    def clean(self, s):
        try:
            return s.strip().replace(';', ',')
        except:
            return None
