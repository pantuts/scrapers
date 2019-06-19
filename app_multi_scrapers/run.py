#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import sys

from websites import SCRAPERS


if len(sys.argv) == 2:
    cmd = sys.argv[1]
    if cmd == 'list':
        pass
    else:
        SCRAPERS[cmd].get_data()
elif len(sys.argv) == 3:
    # rescraping links with error
    cmd = sys.argv[1]
    arg = sys.argv[2]
    SCRAPERS[cmd].get_data(arg)
else:
    # do not run these automatically, need manual checks
    excludes = [
        'financeonline',
        'g2crowd',
        'salesforce2'
    ]
    for e in excludes:
        del SCRAPERS[e]

    MODULES = [v for k, v in SCRAPERS.items()]
    for m in MODULES:
        m.get_data()

