#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException

import csv
import re
import time

import socket
socket.setdefaulttimeout(360)


MAIN_URL = 'http://www.oklahomacounty.org/assessor/Searches/MapNumber.asp'
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.4 '
USER_AGENT += '(KHTML, like Gecko) Chrome/5.0.370.0 Safari/533.4'
PAGINATION_ERROR_COUNT = 0
PAGINATION = True


def generate_filename(fname):
    return fname + '_' + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%I-%M')


def log_data(log):
    with open('log.txt', 'a+') as f:
        f.write(log + '\n')


def write_csv(csv_fname, data):
    try:
        with open(csv_fname, 'a+') as f:
            writer = csv.writer(f)
            for d in data:
                writer.writerow([e for e in d])
                f.flush()
    except Exception as e:
        print('[-] CSV ERROR: ', str(e))


def get_accounts(soup):
    try:
        data = []
        accounts = soup.find_all('a', attrs={'href': re.compile(r'ACCOUNTNO')})
        if accounts:
            for acc in accounts:
                profile = 'http://www.oklahomacounty.org/assessor/Searches/' + \
                    acc.get('href').strip()
                if 'ACCOUNTNO' not in profile:
                    continue
                account = acc.get_text().strip()
                data.append([account, profile])
        return data
    except Exception as e:
        print('[-] GET ACCOUNTS ERROR: ', str(e))
        return None


def main(csv_fname, url=None, current_page=None):
    global PAGINATION_ERROR_COUNT
    url = url if url else MAIN_URL
    current_page = current_page if current_page else 0
    try:
        print('[+] Getting source for page: ' + str(current_page + 1))

        desired_capabilities = dict(DesiredCapabilities.PHANTOMJS)
        desired_capabilities["phantomjs.page.settings.userAgent"] = (
            USER_AGENT)
        desired_capabilities['phantomjs.page.settings.webStorageEnabled'] = True
        desired_capabilities['phantomjs.page.settings.browserConnectionEnabled'] = True
        desired_capabilities['phantomjs.page.settings.locationContextEnabled'] = True
        desired_capabilities['phantomjs.page.settings.applicationCacheEnabled'] = True

        driver = webdriver.PhantomJS(desired_capabilities=desired_capabilities)
        driver.set_page_load_timeout(360)
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'lxml')
        data = get_accounts(soup)
        if data:
            write_csv(csv_fname, data)
            for d in data:
                print('[+] Done >>> ' + d[0])
                log_data(d[0] + ' - ' + d[1])
            current_page = current_page + 1
            log_data('------------------------%s------------------------' %
                     str(current_page))

            while PAGINATION:
                if PAGINATION_ERROR_COUNT == 5:
                    # means all is done
                    return False
                xpth = '/html/body/div[2]/table/tbody/tr[3]/td[2]/table/tbody/tr[26]/td/form/nobr/input[3]'
                nxt = driver.find_element_by_xpath(xpth)
                if nxt:
                    nxt.click()
                    soup1 = BeautifulSoup(driver.page_source, 'lxml')
                    data1 = get_accounts(soup1)
                    if data1:
                        write_csv(csv_fname, data1)
                        for d in data1:
                            print('[+] Done >>> ' + d[0])
                            log_data(d[0] + ' - ' + d[1])
                        current_page = current_page + 1
                        log_data(
                            '------------------------%s------------------------' % str(current_page))
                    PAGINATION_ERROR_COUNT = 0
                else:
                    PAGINATION_ERROR_COUNT = PAGINATION_ERROR_COUNT + 1
        else:
            main(csv_fname, url=url, current_page=current_page)
    except Exception as e:
        print('[-] ERROR: Will retry...')
        print('[-] ' + str(e))
        print()
        main(csv_fname, url=url, current_page=current_page)


if __name__ == '__main__':
    CSV_FNAME = generate_filename('OKC_SEARCH') + '.csv'
    main(CSV_FNAME)
