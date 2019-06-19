#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

from bs4 import BeautifulSoup
from configs import *
from utils import request


class DribbbleDesigners:
    def __init__(self):
        pass

    def write_str(self, fname, _str):
        with open(fname, 'a+') as f:
            f.write(_str + '\n')

    def get_designers(self):
        page = 1
        err_count = 0
        pagination = True
        pagination_err_count = 0
        while pagination:
            url = DESIGNERS_URL.format(page)
            resp = request(url)
            if resp:
                if PAGINATION_DONE_STR.lower() in resp.text:
                    pagination = False

                soup = BeautifulSoup(resp.text, 'lxml')

                lis = soup.select('li.player')
                if lis:
                    err_count = 0

                    for li in lis:
                        h2 = li.find('h2')
                        a = h2.find('a')
                        name = a.get_text().strip()
                        href = MAIN_URL + a.get('href').strip()
                        _str = name + ' <-> ' + href
                        self.write_str(os.path.join(DATA_DIR, FILE_DESIGNERS), _str)
                        print('[+] {}'.format(name))
                else:
                    err_count = err_count + 1
                    if err_count == 5:
                        break
            else:
                pagination_err_count = pagination_err_count + 1
                if pagination_err_count == 5:
                    break
            page = page + 1
