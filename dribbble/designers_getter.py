#!/usr/bin/python
# -*- coding: utf-8 -*-
# by: pantuts

# DISCLAIMER: FOR TESTING AND EDUCATIONAL PURPOSES ONLY
# ANYTHING YOU DO WILL NOT AND SHOULD NOT AND CANNOT AFFECT THE AUTHOR, BE RESPONSIBLE!

from bs4 import BeautifulSoup
from configs import *
from designer import Designer
from shots import Shots
from utils import create_folder, request, write_csv


class DesignersProfiles:
    def __init__(self):
        self.designers = [s.strip() for s in open(os.path.join(DATA_DIR, FILE_DESIGNERS)) if s.strip()]
        header = [[
            'Name', 'Username', 'Profile', 'Shots', 'Projects',
            'Followers', 'Likes', 'Tags', 'Email', 'Website',
            'Instagram', 'Facebook', 'Twitter', 'Linkedin', 'Vimeo'
        ]]
        write_csv(header, DATA_DIR, CSV_DESIGNERS)

    def get_profiles(self):
        for count, des in enumerate(self.designers):
            count = count + 1

            _des = des.split('<->')
            name = _des[0].replace(';', '').strip()
            url = _des[1].strip()
            username = url.rpartition('/')[-1]

            des_folder = os.path.join(DATA_DIR, str(count) + '_' + username)
            create_folder(des_folder)

            resp = request(url)
            if resp:
                soup = BeautifulSoup(resp.text, 'lxml')
                if soup:
                    des = Designer(soup)
                    shots = des.shots()
                    projs = des.projects()
                    flw = des.followers()
                    likes = des.likes()
                    tags = des.tags()
                    email = des.email()
                    site = des.website()
                    ins = des.instagram()
                    fb = des.facebook()
                    tw = des.twitter()
                    ln = des.linkedin()
                    vm = des.vimeo()

                    data = [[
                        name, username, url,
                        shots, projs,
                        flw, likes, tags,
                        email, site,
                        ins, fb, tw, ln, vm
                    ]]
                    write_csv(data, DATA_DIR, CSV_DESIGNERS)
                    print('[+] Done >> {}'.format(username))

                    if shots > 0:
                        sh = Shots(des_folder, shots, username)
                        sh.get_shots()
