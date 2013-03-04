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

from .validators import ConnectionData, QueryData, LdapData, null

from pyramid_ldap import (ldap_setup, ldap_set_login_query,
                          get_ldap_connector_name)

import ldap

class FormatInterpolator(str):
    """A utility class allowing the % operator to format a PEP 3101
    format string

    >>> f = FormatInterpolator('{one} -> {two}')
    >>> f
    <FormatInterpolator('{one} -> {two}')>

    >>> f % {'one': 1, 'two': 2}
    '1 -> 2'

    >>> f.format(one=1, two=2)
    '1 -> 2'

    >>> f % (1,2)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "interp.py", line 33, in __mod__
        raise TypeError('format requires a mapping')
    TypeError: format requires a mapping

    >>> f % {'one': 1}
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "interp.py", line 22, in __mod__
        return self.tpl.format(**other)
    KeyError: 'two'

    >>> f % {'one': 1, 'two': 2, 'three': 3}
    '1 -> 2'

    >>> f = FormatInterpolator('{} {} {}')
    >>> f % (1, 2, 3)
    '1 2 3'

    >>> f.format(1, 2, 3)
    '1 2 3'

    >>> f % (1, 2,)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "formatters.py", line 86, in __mod__
        raise TypeError('not enough arguments for format string')
    TypeError: not enough arguments for format string

    >>> f = FormatInterpolator('{one} -> {two}')
    >>> True if f else False
    True
    >>>
    >>> f = FormatInterpolator('')
    >>> True if f else False
    False

    """

    def __repr__(self):
        return '<FormatInterpolator(%s)>' % str.__repr__(self)

    def __mod__(self, other):

        if isinstance (other, dict):
            try:
                return self.format(**other)
            except IndexError:
                raise TypeError('not enough arguments for format string')

        try:
            if isinstance(other, tuple):
                return self.format(*other)
            else:
                return self.format(str(other))

        except KeyError:
            raise TypeError('format requires a mapping')
        except IndexError:
            raise TypeError('not enough arguments for format string')


def _activity_identifier(base_identifier, name=''):
    if name:
        return '-'.join((base_identifier, name))
    else:
        return base_identifier

def _registry_identifier(base_identifier, name=''):
    if name:
        return '_'.join((base_identifier, name))
    else:
        return base_identifier

class AlwaysOk(object):

    def __init__(self, **kw):
        pass

    def authenticate(self, request, userid, password):
        return {'cf':'xyxyx'}

class FixedCredentials(AlwaysOk):

    def __init__(self, **kw):
        self.userid = kw.get('userid','')
        self.password = kw.get('password','')

    def authenticate(self, request, userid, password):
        if self.userid == userid and self.password == password:
            return {'cf': "%s's cf" % s}
        return {}

class AlwaysFail(AlwaysOk):

    def authenticate(self, request, userid, password):
        return {}

def _register_internal_backend(config, cls, name, **parms):

    conn_name = _registry_identifier('velruse_auth_connector', name)
    intr_name = _registry_identifier('velruse_auth', name)
    act_name = _activity_identifier('velruse-auth', name)


    def get_connector(request):
        registry = request.registry
        connector = cls(**parms)
        return connector

    config.set_request_property(get_connector, conn_identif, reify=True)

    intr = config.introspectable(
        '%s setup' % intr_identif,
        None,
        pprint.pformat(**kw),
        '%s setup' % intr_identif,
        )

    config.action(act_identif, None, introspectables=(intr,))
    return conn_name

def alwaysok(config, name='alwaysok', **kw):
    return _register_internal_backend(config, AlwaysOk, name, **kw)

def alwaysfail(config, name='alwaysfail', **kw):
    return _register_internal_backend(config, AlwaysFail, name, **kw)

def fixedcreds(config, name='fixedcreds', **kw):
    return _register_internal_backend(config, FixedCredentials, name, **kw)

def ldapauth(config, uri, base_dn, filter_tmpl, name='ldap',
             connection_parms=None, query_parms=None):

    connection_parms = connection_parms or {}
    query_parms = query_parms or {}
    connection_parms['context'] = name
    query_parms['context'] = name

    """ ldap_setup(config, uri, bind=None, passwd=None,
                         pool_size=10, retry_max=3, retry_delay=.1,
                         use_tls=False, timeout=-1, use_pool=True,
                         base_dn='', filter_tmpl='',
                         scope=ldap.SCOPE_ONELEVEL, cache_period=0,
                         search_after_bind=False,
                         name=''):

    
        ldap_set_login_query(config, base_dn, filter_tmpl, 
                          scope=ldap.SCOPE_ONELEVEL, cache_period=0,
                          search_after_bind=False, context='')
                          get_ldap_connector_name
    """

    ldap_setup(config, uri, **connection_parms)
    ldap_set_login_query(config, base_dn, filter_tmpl, **query_parms)

    return get_ldap_connector_name(name)

