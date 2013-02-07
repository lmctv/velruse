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

class FormAuthOK(AuthenticationComplete):
    """USER auth complete"""
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

class FormAuthFail(AuthenticationDenied):
    """USER auth denied"""
    def __init__(self, reason=None,
                 provider_name=None,
                 provider_type=None,
                 endpoint=None):
        self.reason = reason
        self.provider_name = provider_name
        self.provider_type = provider_type
        if endpoint:
            self.endpoint = endpoint


def add_form_login(config,
                      attribute_mappings= None,
                      host_whitelist = None,
                      host_blacklist = None,
                      name='form_login'):
    """
    Add a local form login provider to the application.
    """

    login_path = '/%s/login' % name
    result_path = '/%s/results' % name

    provider = FormProvider(name, login_path, result_path,
                             attribute_mappings=attribute_mappings,
                             host_whitelist=host_whitelist,
                             host_blacklist=host_blacklist,
                             connector_key=connector_key,
                            )

    config.add_route(provider.login_route, login_path)
    config.add_view(provider, attr='login', route_name=provider.login_route,
                    permission=NO_PERMISSION_REQUIRED,
                    renderer='velruse:templates/form_login.mako')
    config.add_route(provider.result_route, result_path,
                     use_global_views=True,
                     factory=provider.result)

    register_provider(config, name, provider)


class FormProvider(object):

    def __init__(self, name, attribute_mappings=None,
                    host_whitelist=None, host_blacklist=None,
                    connector_key=''):

        self.name = name
        self.connector_key=connector_key
        self.uri = uri
        self.type = 'velruse_form'
        self.login_route = '%s/login' % self.name
        self.result_route = '%s/result' % self.name

    def login(self, request):
        """Show a login form to the user"""
        parms = {}
        parms['endpoint'] = request.POST.get('endpoint', '')
        parms['auth_session_key'] = request.POST.get('auth_session_key','')
        return parms

    def result(self, request):
        """Initiate a User login"""
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
            return FormAuthOK(profile=userdata, credentials={},
                              provider_name=self.name,
                              provider_type=self.type, endpoint=endpoint)

        log.debug('auth fail')
        return FormAuthFail(provider_name=self.name, provider_type=self.type,
                            endpoint=endpoint)



def _add_form_login_from_settings(config, prefix='velruse.forms.'):
    settings = config.registry.settings
    p = ProviderSettings(settings, prefix)
    p.update('name')
    p.update('attribute_mappings')
    p.update('host_whitelist')
    p.update('host_blacklist')
    p.update('backend')
    config.add_form_login(**p.kwargs)


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


def attach_named_backend(config, cls_setup, name='backend', *args, **kw):

    connector = cls_setup( *args, **kw)

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



def includeme(config):
    config.add_directive('add_form_login', add_form_login)

    if 'velruse.providers.localform' in config.registry.settings['pyramid.includes']:
        _add_form_login_from_settings(config)

