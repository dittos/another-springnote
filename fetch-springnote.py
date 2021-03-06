#!/usr/bin/env python3
from __future__ import print_function

import os
import errno
import sys

import json

from springnote import Springnote, SpringnoteException

try:
    raw_input
    input = raw_input
except: pass

def makedirs(path, exist_ok=False):
    try:
        os.makedirs(path)
    except OSError, e:
        if e.errno == errno.EEXIST and exist_ok:
            pass
        else: raise

class Fetcher:
    def __init__(self):
        openid = input('Your OpenID (like http://example.myid.net/) : ')
        print('''Go to following URL and get the user key:
https://api.openmaru.com/delegate_key/springnote?app_id=71fcb7c8'''
            '&openid={}'.format(openid))
        key = input('Key: ')
        print('Connecting...')
        self.api = Springnote(openid, key)

    SAVE_PATH = '_api'

    def fetch(self, path):
        assert '..' not in path
        cache_path = os.path.normpath(self.SAVE_PATH + path)
        if os.access(cache_path, os.F_OK):
            return open(cache_path, 'rb').read()
        makedirs(os.path.split(cache_path)[0], exist_ok=True)
        try:
            data = self.api._fetch('GET', path)
        except SpringnoteException as ex:
            if ex.status in [404]:
                return None
            raise
        open(cache_path, 'wb+').write(data)
        return data


def main():
    bot = Fetcher()
    pages = json.loads(bot.fetch('/pages.json').decode('ascii'))
    print('\r{} / {} pages'.format(0, len(pages)), end='')
    for i, entry in enumerate(pages):
        id_ = entry['page']['identifier']
        bot.fetch('/pages/{}.json'.format(id_))
        for resource in ['collaboration', 'comments', 'revisions']:
            bot.fetch('/pages/{}/{}.json'.format(id_, resource))
        attachments = bot.fetch('/pages/{}/attachments.json'.format(id_))
        if attachments:
            for _ in json.loads(attachments.decode('ascii')):
                bot.fetch('/pages/{}/attachments/{}'.format(id_, _['attachment']['identifier']))
        print('\r{} / {} pages'.format(i + 1, len(pages)), end='')
    print('')
    tags = json.loads(bot.fetch('/tags.json').decode('ascii'))
    return
    print('\r{} / {} tags'.format(0, len(tags)), end='')
    for i, entry in enumerate(tags):
        id_ = entry['tag']['identifier']
        bot.fetch('/tag/{}.json'.format(id_))
        print('\r{} / {} tags'.format(i + 1, len(tags)), end='')
    print('')


if __name__ == '__main__':
    main()
