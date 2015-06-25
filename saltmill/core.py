# -*- coding: utf-8 -*-
import os
from functools import wraps
import time
import ConfigParser

import pepper


def login_required(func):
    @wraps(func)
    def func_wrapper(self, *args, **kwargs):
        if not getattr(self, 'auth', None):
            self.login()
        elif time.time() > self.auth['expire']:
            self.login()
        func(self, *args, **kwargs)
    return func_wrapper


class Mill(object):
    def __init__(self, debug_http=False, *args, **kwargs):
        self.configure(**kwargs)
        self.pepper = pepper.Pepper(self.login_details['SALTAPI_URL'],
                                    debug_http=debug_http)

    def configure(self, **kwargs):
        '''
        Get salt-api login configurations.
        Source & order:
        kwargs > environment variables > ~/.pepperrc
        '''
        # default settings
        details = {
            'SALTAPI_URL': 'https://localhost:8000/',
            'SALTAPI_USER': 'saltdev',
            'SALTAPI_PASS': 'saltdev',
            'SALTAPI_EAUTH': 'auto',
        }

        # read from ~/.pepperrc
        config = ConfigParser.RawConfigParser()
        config.read(os.path.expanduser('~/.pepperrc'))
        profile = 'main'
        if config.has_section(profile):
            for key, value in config.items(profile):
                key = key.upper()
                details[key] = config.get(profile, key)

        # get environment values
        for key, value in details.items():
            details[key] = os.environ.get(key, details[key])

        # get Mill().__init__ parameters
        for key, value in details.items():
            details[key] = kwargs.get(key.lower().lstrip('saltapi_'),
                                      details[key])

        self.login_details = details

    def login(self):
        '''
        simple wrapper for Pepper.login()
        '''
        self.auth = self.pepper.login(
            self.login_details['SALTAPI_USER'],
            self.login_details['SALTAPI_PASS'],
            self.login_details['SALTAPI_EAUTH'],
        )