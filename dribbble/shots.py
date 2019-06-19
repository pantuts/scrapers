#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import os
import re
from bs4 import BeautifulSoup
from configs import *
from utils import create_folder, request, write_csv, download


class Shots:
    def __init__(self, des_folder, shots_count, username):
        self.shots_count = shots_count
        self.username = username
        self.shots_folder = os.path.join(des_folder, 'shots')
        create_folder(self.shots_folder)

    def get_shots(self):
        shots_count = 0
        page = 1
        pagination = True
        pagination_err_count = 0
        while pagination:
            if shots_count >= self.shots_count:
                break

            url = SHOTS_PAGINATION.format(self.username, page)
            resp = request(url)
            if resp:
                soup = BeautifulSoup(resp.text, 'lxml')
                if soup:
                    lis = soup.find_all('li', id=re.compile(r'screenshot-[0-9]'))
                    for li in lis:
                        shots_count = shots_count + 1

                        pic = None
                        ext = None
                        comment = None
                        timestamp = None

                        div = li.find('div', class_='dribbble-shot')
                        link = div.find('a', class_='dribbble-link')
                        shot_url = MAIN_URL + link.get('href').strip()
                        try:
                            pic = link.find('picture').find('source').get('srcset').strip()
                        except Exception:
                            pass
                        if pic:
                            ext = pic.rpartition('/')[-1].rpartition('.')[-1]
                        drib = div.find('a', class_='dribbble-over')
                        shot = drib.find('strong').get_text().replace(';', '').strip()
                        try:
                            comment = drib.find('span', class_='comment').get_text().replace(';', '').strip()
                        except Exception:
                            pass

                        fname_pic = '{}_{}.{}'.format(str(shots_count), shot.replace(' ', '_').lower(), ext)
                        if os.path.exists(os.path.join(self.shots_folder, fname_pic)):
                            dl = True
                        else:
                            dl = download(pic, self.shots_folder, fname_pic)
                        data = [[shot, comment, shot_url, fname_pic if dl else None]]
                        write_csv(data, self.shots_folder, 'shots.csv')
                        print('[+] Done >> {}'.format(shot))
            else:
                pagination_err_count = pagination_err_count + 1
                if pagination_err_count == 5:
                    break
            page = page + 1
