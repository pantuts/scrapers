#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import os

# GENERAL
DIR_MODE = 0o0755
THREAD_WORKERS = 10

# DIR
ROOT_DIR = './data'
CSV_DIR = os.path.join(ROOT_DIR, 'csv')

# REQUESTS
MAX_ATTEMPTS = 5
MAX_DELAYS = 5
MAX_TIMEOUT = 50
HEADERS = {
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US;q=0.9,en;q=0.8',
    'cache-control': 'max-age=0',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}
ACCEPT = {
    'html': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'json': 'application/javascript, application/json',
}

# LOGS
LOG_FILENAME = 'logfile.log'
LOG_DIR = os.path.join(ROOT_DIR, 'logs')
LOG_FORMAT = '%(asctime)s [PID %(process)d] [%(levelname)s] %(name)s -> %(message)s'
LOG_MAX_SIZE_BYTES = 5e+6
LOG_BACKUP_COUNT = 3

