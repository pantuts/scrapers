#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: github.com/pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

import os
from configs import *
from designers_getter import DesignersProfiles
from designers_list import DribbbleDesigners


if __name__ == '__main__':
    drb = DribbbleDesigners()
    drb.get_designers()

    if os.path.exists(os.path.join(DATA_DIR, FILE_DESIGNERS)):
        dp = DesignersProfiles()
        dp.get_profiles()
