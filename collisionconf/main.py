#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import csv
import requests
import sys
import time
from datetime import datetime


class CollisionAttendees:
    def __init__(self):
        self.fname = 'attendees_' + \
            datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %I:%M')
        self.url = 'https://api.cilabs.net/v1/conferences/cc16/info/attendees?page='
        self.empty_count = 0

    def request(self, url):
        headers = {
            'origin': 'https://collisionconf.com',
            'referer': 'https://collisionconf.com/attendees/featured-attendees',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'
        }
        try:
            print('Getting json: ' + url)
            req = requests.get(url, headers=headers)
            return req.json()
        except Exception as e:
            print('Unable to get json.')
            print(str(e))
            self.log('[-] ERROR: Unable to get json. >>> PAGE: ' +
                     url[url.index('=') + 1:])
            return False

    def log(self, log_str):
        t = time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime()) + ' : '
        t += log_str
        with open(self.fname + '.log', 'a+') as f:
            f.write(t + '\n')

    def get_data(self):
        for i in range(200):
            self.log('>>> PAGE: ' + str(i + 1))
            jsn_data = self.request(self.url + str(i + 1))
            if jsn_data:
                if jsn_data.get('attendees'):
                    items = jsn_data['attendees']
                    if len(items) > 0:
                        for item in items:
                            name = self.get_name(item)
                            bio = self.get_bio(item)
                            career = self.get_career(item)
                            company = self.get_company(item)
                            country = self.get_country(item)
                            data = [[name, bio, career, company, country]]
                            self.write_csv(data)
                else:
                    print('No data for page: ' + str(i + 1))
                    self.log('[-] No data. >>> PAGE: ' + str(i + 1))
                    self.empty_count = self.empty_count + 1
                    if self.empty_count == 7:
                        break
            print('Done')
        sys.exit(0)

    def get_name(self, item):
        try:
            return item['name'].strip()
        except:
            return 'Undefined'

    def get_bio(self, item):
        try:
            return item['bio'].strip().replace(';', '')
        except:
            return 'Undefined'

    def get_country(self, item):
        try:
            return item['country'].strip().replace(';', '')
        except:
            return 'Undefined'

    def get_company(self, item):
        try:
            return item['company'].strip().replace(';', '')
        except:
            return 'Undefined'

    def get_career(self, item):
        try:
            return item['career'].strip().replace(';', '')
        except:
            return 'Undefined'

    def write_csv(self, data):
        for d in data:
            with open(self.fname + '.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([e for e in d])
                f.flush()


if __name__ == '__main__':
    try:
        ca = CollisionAttendees()
        ca.get_data()
    except KeyboardInterrupt:
        print('Interrupted.')
