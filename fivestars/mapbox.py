#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

from configs import MAPBOX_TOKEN, MAPBOX_URL
from utils import request


class Mapbox:
    def __init__(self, city):
        self.city = city

    def get_point(self):
        headers = {
            'Origin': 'https://www.fivestars.com',
            'Referer': 'https://www.fivestars.com/locations/'
        }
        resp = request(MAPBOX_URL.format(self.city, MAPBOX_TOKEN), headers=headers)
        if resp:
            jsn = resp.json()
            features = jsn.get('features')
            if features:
                for feat in features:
                    place_type = feat.get('place_type')
                    if place_type:
                        if 'place' in place_type:
                            geo = feat.get('geometry').get('coordinates')
                            lon = geo[0]
                            lat = geo[1]
                            return {'latitude': lat, 'longitude': lon}
            return None
        return None
