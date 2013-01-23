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

class LdapAuthOK(AuthenticationComplete):
    """LDAP auth complete"""
    def __init__(self, profile=None,
                 credentials=None,
                 provider_name=None,
                 provider_type=None,
                 endpoint=None):
        self.profile = profile
        self.credentials = credentials
        self.provider_name = provider_name
        self.provider_type = provider_type
        if endpoint:
            self.endpoint = endpoint

class LdapAuthFail(AuthenticationDenied):
    """LDAP auth denied"""
    def __init__(self, reason=None,
                 provider_name=None,
                 provider_type=None,
                 endpoint=None):
        self.reason = reason
        self.provider_name = provider_name
        self.provider_type = provider_type
        if endpoint:
            self.endpoint = endpoint

def _add_ldap_login_from_settings(config, prefix='velruse.ldap.'):
    settings = config.registry.settings
    p = ProviderSettings(settings, prefix)
    p.update('name')
    p.update('attribute_mappings')
    p.update('host_whitelist')
    p.update('host_blacklist')
    return
    config.add_ldap_login(**p.kwargs)


def add_ldap_login(config,
                      attribute_mappings= None,
                      host_whitelist = None,
                      host_blacklist = None,
                      connector_key = 'ldap_connector',
                      name='ldap'):
    """
    Add a LDAP login provider to the application.
    """

    login_path = '/login/%s' % name
    result_path = '/login/%s/result' % name

    provider = LdapProvider(name, login_path, result_path,
                             attribute_mappings=attribute_mappings,
                             host_whitelist=host_whitelist,
                             host_blacklist=host_blacklist,
                             connector_key=connector_key,
                            )

    config.add_route(provider.login_route, login_path)
    config.add_view(provider, attr='login', route_name=provider.login_route,
                    permission=NO_PERMISSION_REQUIRED,
                    renderer='velruse:templates/ldap_login.mako')
    config.add_route(provider.result_route, result_path,
                     use_global_views=True,
                     factory=provider.result)

    register_provider(config, name, provider)


class LdapProvider(object):

    def __init__(self, name, attribute_mappings=None,
                    host_whitelist=None, host_blacklist=None,
                    connector_key=''):

        self.name = name
        self.connector_key=connector_key
        self.uri = uri
        self.type = 'pyramid_ldap'
        self.login_route = '%s/login' % self.name
        self.result_route = '%s/result' % self.name

    def login(self, request):
        """Show a login form to the user"""
        parms = {}
        parms['endpoint'] = request.POST.get('endpoint', '')
        parms['auth_session_key'] = request.POST.get('auth_session_key','')
        return parms
        
    def result(self, request):
        """Initiate a LDAP login"""
        login = request.POST.get('login', '')
        password = request.POST.get('password', '')
        endpoint = request.POST.get('endpoint', '')
        auth_session_key = request.POST.get('auth_session_key','')

        conn = getattr(request, self.connector_key, None)
        if connector is None:
            raise Exception('connector %s not found in request attribute' % 
                            self.connector_key)

        userentry = conn.authenticate(login, password)

        if userentry is not None:
            return LdapAuthOK(profile=userdata, credentials={},
                              provider_name=self.name,
                              provider_type=self.type, endpoint=endpoint)

        log.debug('auth fail')
        return LdapAuthFail(provider_name=self.name, provider_type=self.type,
                            endpoint=endpoint)


def includeme(config):
    config.add_directive('add_ldap_login', add_ldap_login)

    if 'velruse.providers.ldap' in config.registry.settings['pyramid.includes']:
        _add_ldap_login_from_settings(config)

