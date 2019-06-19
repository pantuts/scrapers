#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import csv
import re
import time
import sys

from postal_codes import POSTAL_CODES


def get_data(soup):
    name = soup.find('h1').get_text().strip().title()
    p = soup.find('h1').find_next('p', class_='grau').find_next('p')
    for br in p.find_all('br'):
        br.replaceWith('\n')
    for a in p.find_all('a'):
        a.replaceWith('')
    addr = ', '.join([i.strip()
                      for i in p.get_text().split('\n') if i.strip()])
    div = soup.find('strong', text=re.compile(r'Telefon')).find_next('div')
    phone = div.next
    site = div.find('a')
    if site:
        site = site.get('href')
        if site.startswith('/'):
            site = None
    return [name, addr, phone, site]


def write_csv(data, fname):
    try:
        with open(fname, 'a') as f:
            writer = csv.writer(f)
            for d in data:
                writer.writerow([e for e in d])
                f.flush()
    except Exception as e:
        print('[-] CSV ERROR: {}'.format(e))


URL_DERMA = 'https://www.jameda.de/aerzte/hautaerzte-dermatologen-geschlechtskrankheiten/fachgebiet/'
URL_NEPHRO = 'https://www.jameda.de/aerzte/nephrologen-nierenerkrankungen/fachgebiet/'
CSV_DERMA = 'Dermatologists.csv'
CSV_NEPHRO = 'Nephorologists.csv'
PROFILES = []

term = sys.argv[1]
if term == 'derma':
    url = URL_DERMA
    csv_fname = CSV_DERMA
if term == 'nephro':
    url = URL_NEPHRO
    csv_fname = CSV_NEPHRO


driver = webdriver.Chrome()
driver.get(url)
time.sleep(1)

for pcode in POSTAL_CODES:
    print('---------------------------------START: {}---------------------------------'.format(pcode))
    soup = BeautifulSoup(driver.page_source, 'lxml')
    where_id = soup.find('div', text='Ort, PLZ, Stadtteil oder Straße').find_previous(
        'div').find('input').get('id')
    where_input = driver.find_element_by_id(where_id)
    select = Select(driver.find_element_by_name('dist'))
    select.select_by_value('50')
    where_input.clear()
    where_input.send_keys(pcode)
    where_input.send_keys(Keys.RETURN)

    while True:
        try:
            more = driver.find_element_by_id('more_results_link')
            if more:
                more.click()
                time.sleep(2)
            else:
                break
        except Exception as e:
            break

    # soup = BeautifulSoup(driver.page_source, 'lxml')
    h2s = driver.find_elements_by_tag_name('h2')
    try:
        for i, h2 in enumerate(h2s):
            h2.find_element_by_tag_name('a').send_keys(
                Keys.CONTROL + Keys.RETURN)
            driver.switch_to_window(driver.window_handles[1])
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            locs = soup.select('div.ergebnis')
            if len(locs) > 0 or len(locs) == 2:
                h2s_2 = driver.find_elements_by_tag_name('h2')
                try:
                    for h2_2 in h2s_2:
                        h2_2.find_element_by_tag_name('a').send_keys(
                            Keys.CONTROL + Keys.RETURN)
                        driver.switch_to_window(driver.window_handles[2])
                        time.sleep(2)

                        soup = BeautifulSoup(driver.page_source, 'lxml')
                        data = get_data(soup)

                        write_csv([data], csv_fname)
                        print('>> {}'.format(data[0]))

                        driver.close()
                        driver.switch_to_window(driver.window_handles[1])
                        time.sleep(1)
                    driver.switch_to_window(driver.window_handles[0])
                except Exception as e:
                    if len(driver.window_handles) > 1:
                        for w in driver.window_handles[1:]:
                            driver.switch_to_window(w)
                            driver.close()
                    driver.switch_to_window(driver.window_handles[0])
            else:
                soup = BeautifulSoup(driver.page_source, 'lxml')
                data = get_data(soup)

                write_csv([data], csv_fname)
                print('>> {}'.format(data[0]))

                driver.close()
                driver.switch_to_window(driver.window_handles[0])
    except Exception as e:
        pass

    print('---------------------------------END: {}---------------------------------'.format(pcode))

    try:
        driver.find_element_by_partial_link_text('Ort ändern').click()
    except:
        pass

driver.quit()
