#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

#################
# I cut the code, yep, you must have your own utils.
#################

import config
import csv
import daiquiri
import daiquiri.formatter
import json
import logging
import os
import re
import requests
import sys
import uuid

from datetime import datetime
from pythonjsonlogger import jsonlogger
from tenacity import retry, stop_after_attempt, stop_after_delay, TryAgain
from xml.dom import minidom

REQUEST_SESSION = None


def setup_logger():
    pass


def request():
    pass


class FileDirectoryUtils:
    def create_dir(self):
        pass

    def touch(self):
        pass


class CSVUtils:
    pass


def get_sitemap_set():
    pass


def get_sitemap_locs():
    pass


fdu = FileDirectoryUtils()
fdu.create_dir(config.ROOT_DIR)
fdu.create_dir(config.LOG_DIR)

NOW = datetime.strftime(datetime.now(), '%Y-%m-%d')
fdu.create_dir(os.path.join(config.CSV_DIR, NOW))

logfile = os.path.join(config.LOG_DIR, f'{config.LOG_FILENAME}')
fdu.touch(logfile)
logger = setup_logger(__name__)
