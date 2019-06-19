#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import csv
import re
import requests
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from maxprep_filters import DIVISIONS, RANKINGS_BY_DIVISION, RANKINGS_URL
from maxpreps import FootballProfile, FootballMap
from result_parser import RowParser, ProfileParser, get_state_class
from utils import get_cookies, request, generate_filename, write_csv


def scrape(division=False, csv_file=None, newcol=False):
    csv_fname = generate_filename('MAXPREPS') + '.csv'
    cookies = get_cookies()
    s = requests.Session()

    done_text = 'We do not have rankings for this selection, please try another search'

    if not division:
        pagination = True
        cur_page = 1
        while pagination:
            soup = request(s, RANKINGS_URL.format(cur_page), cookies)
            if soup:
                if done_text in str(soup):
                    break
                else:
                    print('-----------------------Page {}-----------------------'.format(cur_page))
                    cur_page = cur_page + 1

                    try:
                        trs = soup.select('table tr')[1:]
                    except:
                        trs = []

                    for tr in trs:
                        rp = RowParser(tr)
                        name = rp.get_name()
                        rating = rp.get_rating()
                        strength = rp.get_strength()
                        p_url = rp.get_profle_url()
                        s_num = rp.get_search_num()

                        prof_soup = request(s, p_url, cookies)
                        if soup:
                            pp = ProfileParser(
                                s, cookies, prof_soup,
                                s_num, name, rating, strength, p_url
                            )
                            data = pp.get_data()
                            write_csv(csv_fname, data)
                            print('[+] Done >> {}'.format(name))
    else:
        # this is just for added state class/ranks cols
        if newcol:
            with open(csv_file, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    name = row[5]
                    url = row[4]
                    soup = request(s, url, cookies)
                    if soup:
                        fp = FootballProfile(name, soup)
                        data = [[
                            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                            row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15],
                            row[16], row[17], row[18], fp.state_class_division_name(), fp.state_division_rank()
                        ]]
                        write_csv('__' + csv_file, data)
                        print('[+] Done >> {}'.format(name))
        else:
            for div in DIVISIONS:
                print('-----------------------DIVISION: {}-----------------------'.format(div))
                state_soup = request(s, RANKINGS_BY_DIVISION.format(1, div), cookies)
                if state_soup:
                    state_class = get_state_class(state_soup)
                    if state_class:
                        for sc in state_class:
                            clas_url = sc[1]
                            clas_name = sc[0]
                            print('-----------------------STATE CLASS: {}-----------------------'.format(clas_name))

                            pagination = True
                            cur_page = 1
                            while pagination:
                                # '/rankings/football-fall-16/{}/division/fl/asZCeSbCLkCIkW5UXU_cOw/division-8a.htm'
                                url = re.sub(r'/[0-9]{1,3}/', '/{}/', clas_url)
                                soup = request(s, url.format(cur_page), cookies)
                                if soup:
                                    if done_text in str(soup):
                                        pagination = False
                                    else:
                                        print('-----------------------Page {}-----------------------'.format(cur_page))
                                        cur_page = cur_page + 1

                                        try:
                                            trs = soup.select('table tr')[1:]
                                        except:
                                            trs = []

                                        for tr in trs:
                                            rp = RowParser(tr)
                                            name = rp.get_name()
                                            rating = rp.get_rating()
                                            strength = rp.get_strength()
                                            p_url = rp.get_profle_url()
                                            s_num = rp.get_search_num()

                                            prof_soup = request(s, p_url, cookies)
                                            if soup:
                                                pp = ProfileParser(
                                                    s, cookies, prof_soup,
                                                    s_num, name, rating, strength, p_url
                                                )
                                                data = pp.get_data()
                                                write_csv(csv_fname, data)
                                                print('[+] Done >> {}'.format(name))
                    else:
                        pagination = True
                        cur_page = 1
                        while pagination:
                            soup = request(s, RANKINGS_BY_DIVISION.format(cur_page, div), cookies)
                            if soup:
                                if done_text in str(soup):
                                    pagination = False
                                else:
                                    print('-----------------------Page {}-----------------------'.format(cur_page))
                                    cur_page = cur_page + 1

                                    try:
                                        trs = soup.select('table tr')[1:]
                                    except:
                                        trs = []

                                    for tr in trs:
                                        rp = RowParser(tr)
                                        name = rp.get_name()
                                        rating = rp.get_rating()
                                        strength = rp.get_strength()
                                        p_url = rp.get_profle_url()
                                        s_num = rp.get_search_num()

                                        prof_soup = request(s, p_url, cookies)
                                        if soup:
                                            pp = ProfileParser(
                                                s, cookies, prof_soup,
                                                s_num, name, rating, strength, p_url
                                            )
                                            data = pp.get_data()
                                            write_csv(csv_fname, data)
                                            print('[+] Done >> {}'.format(name))

if __name__ == '__main__':
    if len(sys.argv) <= 3:
        if str(sys.argv[2]) == 'newcol':
            csv_fname = str(sys.argv[1])
            scrape(division=True, csv_file=csv_fname, newcol=True)
        else:
            scrape(division=True)
    else:
        scrape()
