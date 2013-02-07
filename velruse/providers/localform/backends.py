"""Local authentication backends"""
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

from pyramid_ldap import (ldap_setup, ldap_set_login_query,
                          ldap_set_groups_query, get_ldap_connector)

class AllOk(object):

    def __init__(self, userid=None, password=None):
        pass

    def authenticate(self, request, userid, password):
        return True

class FixedCredentials(AllOk):

    def __init__(self, userid=None, password=None):
        self.userid = userid
        self.password = password

    def authenticate(self, request, userid, password):
        return self.userid == userid and self.password == password

class AllFail(AllOk):

    def authenticate(self, request, userid, password):
        return False

class LDAP(object):

    def __init__(self, name=''):
        self.context_name = name

    def authenticate(self, request, userid, password):
        connector = get_ldap_connector(request, context=self.context_name)



def alwaysok(config, name=''):
    pass

def alwaysfail(config, name=''):
    pass

def fixedcreds(config, name=''):
    pass

def pyramid_ldap(config, uri, bind=None, passwd=None,
                         pool_size=10, retry_max=3, retry_delay=.1,
                         use_tls=False, timeout=-1, use_pool=True,
                         base_dn='', filter_tmpl='',
                         scope=ldap.SCOPE_ONELEVEL, cache_period=0,
                         search_after_bind=False,
                         name=''):

    pass



def includeme(config):
    """Setup configurator methods for localform authentication backends"""
    config.add_directive('local_ok_backend_setup', alwaysok)
    config.add_directive('local_fail_backend_setup', alwaysfail)
    config.add_directive('local_fixedcreds_backend_setup', fixedcreds)
    config.add_directive('local_ldap_backend_setup', pyramid_ldap)
