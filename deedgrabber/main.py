#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import csv
import json
import pprint
import re
import requests
from datetime import datetime

REQ_URL = 'http://dc1.parcelstream.com/getByGeometry.aspx?returnGeoType=1&dataSource=DeedGrabber.DMP/ParcelDetail&inclusionGeometries=POINT({} {})'
REQ_URL +='&fields=*&returnFullWkt=true&obsId=window&obsSuccessMethod=S156060657563513301678835&obsErrorMethod=E156060657563513301678835&'
REQ_URL += 'output=json&SS_CANDY=HQjeIYS_Y2iN52psieNucAbLJQIqhK5xHKVNYA~~'


def get_data(lon, lat):
    url = REQ_URL.format(lon, lat)
    print(f'[+] GETTING DATA - ({lon}, {lat})')
    r = requests.get(url)
    if r.status_code >= 200 and r.status_code <= 400:
        try:
            data = json.loads(re.findall(r'(\{.+?\})\)', r.text)[0])
            parcel = data.get('Response').get('Results').get('Data').get('Row')
            submit = {
                'APN': parcel.get('APN'),
                'APN_UNF': parcel.get('APN_UNF'),
                'ACREAGE': parcel.get('ACREAGE'),
                'FIPS_CODE': parcel.get('FIPS_CODE'),
                'GEOMETRY': parcel.get('GEOMETRY'),
                'ADDRESS_ID': parcel.get('ADDRESS_ID'),
                'BUILDING_SQFT': parcel.get(''),
                'LOCATION_ID': parcel.get('LOCATION_ID'),
                'USE_CODE_STD_CTGR_DESC': parcel.get('USE_CODE_STD_CTGR_DESC'),
                'VAL_ASSD_IMPRV': parcel.get('VAL_ASSD_IMPRV'),
                'VAL_ASSD_LAND': parcel.get('VAL_ASSD_LAND'),
                'SITE_ADDR': parcel.get('SITE_ADDR'),
                'SITE_CITY': parcel.get('SITE_CITY'),
                'SITE_PLUS_4': parcel.get('SITE_PLUS_4'),
                'SITE_STATE': parcel.get('SITE_STATE'),
                'SITE_ZIP': parcel.get('SITE_ZIP'),
                'OWNER_ADDRESS': parcel.get('OWNER_ADDRESS'),
                'OWNER_CITY': parcel.get('OWNER_CITY'),
                'OWNER_NAME_1': parcel.get('OWNER_NAME_1'),
                'OWNER_NAME_2': parcel.get('OWNER_NAME_2'),
                'OWNER_STATE': parcel.get('OWNER_STATE'),
                'OWNER_ZIP': parcel.get('OWNER_ZIP'),
                'OWNER_ZIP4': parcel.get('OWNER_ZIP4'),
                'LONGITUDE': lon,
                'LATITUDE': lat
            }
            # pprint.pprint(submit)
            return submit
        except Exception:
            return []
    else:
        return []


def parse_coordinates():
    return [
        tuple([i.strip() for i in s.split(' ') if i.strip()]) \
        for s in open('coordinates.txt').readlines() if s.strip()
    ]


if __name__ == '__main__':
    coordinates = parse_coordinates()
    now = datetime.strftime(datetime.now(), '%Y-%m-%d')

    with open(f'deedgrabber_{now}.csv', 'a+', newline='') as csvfile:
        fieldnames = [
            'APN',
            'APN_UNF',
            'ACREAGE',
            'FIPS_CODE',
            'GEOMETRY',
            'ADDRESS_ID',
            'BUILDING_SQFT',
            'LOCATION_ID',
            'USE_CODE_STD_CTGR_DESC',
            'VAL_ASSD_IMPRV',
            'VAL_ASSD_LAND',
            'SITE_ADDR',
            'SITE_CITY',
            'SITE_PLUS_4',
            'SITE_STATE',
            'SITE_ZIP',
            'OWNER_ADDRESS',
            'OWNER_CITY',
            'OWNER_NAME_1',
            'OWNER_NAME_2',
            'OWNER_STATE',
            'OWNER_ZIP',
            'OWNER_ZIP4',
            'LONGITUDE',
            'LATITUDE'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for c in coordinates:
            data = get_data(c[0], c[1])
            if data:
                writer.writerow(data)
