"""LDAP authentication views"""
import logging

log = logging.getLogger(__name__)

import string

from urlparse import parse_qs

from pyramid.httpexceptions import HTTPFound
from pyramid.security import NO_PERMISSION_REQUIRED

import sys

from velruse.api import (
    AuthenticationComplete,
    AuthenticationDenied,
    register_provider,
)

from velruse.exceptions import ThirdPartyFailure
from velruse.settings import ProviderSettings

from pyramid.settings import aslist

from .validators import ConnectionData, QueryData, null


class AllOk(object):

    def __init__(self, userid=None, password=None):
        pass

    def authenticate(self, userid=None, password=None):
        return True

class FixedCredentials(AllOk):

    def __init__(self, userid=None, password=None):
        self.userid = userid
        self.password = password

    def authenticate(self, userid=None, password=None):
        return self.userid == userid and self.password == password

class AllFail(AllOk):

    def authenticate(self, userid, password):
        return False



def alwaysok(config, name=''):
    pass

def alwaysfail(config, name=''):
    pass

def fixedcreds(config, name=''):
    pass

def pyramid_ldap(config, name=''):
    pass


"""
==========
LDAP setup
==========
"""

def _add_ldap_server_from_settings(config, prefix='velruse.ldapserver'):
    settings = config.registry.settings
    p = ProviderSettings(settings, prefix)

def _add_ldap_backends_from_settings(config):

    backends = config.registry.settings.get('velruse.ldap_backends', None)
    if backends:
        for i in backends:
            p = ProviderSettings(settings, prefix='velruse.%s.' % i)
            print i


def _setup_query_from_setting(config, prefix):

    parm_names = ('templater', 'filter_tmpl', 'scope', 'cache_period',
                  'search_after_bind', )

    settings = config.registry.settings

    _parms = {}

    settings = config.registry.settings

    for key in parm_names:
        _parms[key] = settings.get('%s.%s'(prefix, key), '').strip()

    extractor = ConnectionData()

    try:
        data = extractor.deserialize(_parms)
        logger.debug('data=%r' % data)

    except:
        logger.debug('raw_data=%r' % _parms)


def _setup_connection_from_settings(config, prefix):

    parm_names = ('uri', 'bind', 'passwd', 'pool_size', 'retry_max'
                  'retry_delay', 'use_tls', 'timeout', 'use_pool',)

    _parms = {}

    settings = config.registry.settings

    for key in parm_names:
        _parms[key] = settings.get('%s.%s'(prefix, key), '').strip()

    extractor = ConnectionData()

    try:
        data = extractor.deserialize(_parms)
        logger.debug('data=%r' % data)

    except:
        logger.debug('raw_data=%r' % _parms)


def attach_named_backend(config, cls_setup, name='backend', *args, **args):

    connector = cls_setup( *args, **args)

    def get_connector(request):
        registry = request.registry
        return connector

    

def enable_form_backend(config, factory = None, name = ''):

        if name:
            obj_name = '_'.join(('velruse_form_backend', name))
            intr_name = '_'.join(('velruse_form', context))
            act_name = '-'.join(('velruse-form-back-create', name))

        else:
            obj_name = 'velruse_form_backend'
            intr_name = 'velruse_form'
            act_name = 'velruse-form-back-create'


    key = 'velruse.form_bk.'

    def get_backend(request):
        registry = request.registry
        return backend
    

def enable_form_backends(config):

    backends = config.registry.settings.get('velruse.form_backends')
    if backends:
        pass

