"""LDAP authentication views"""
import logging

CFG_PREFIX = 'velruse.providers.localform'

log = logging.getLogger(__name__)

import string

from urlparse import parse_qs

from pyramid.httpexceptions import HTTPFound
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.settings import aslist

from . import backends

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

from pyramid_ldap import (ldap_setup,
                          ldap_set_login_query,
                          get_ldap_connector)


class FormAuthOK(AuthenticationComplete):
    """USER auth complete"""

class FormAuthFail(AuthenticationDenied):
    """USER auth denied"""

def add_form_login(config,
                      attribute_mapper=None,
                      host_whitelist=None,
                      host_blacklist=None,
                      connector_key=None,
                      name='form_login'):
    """
    Add a local form login provider to the application.
    """

    login_path = '/login/%s' % name
    result_path = '/login/%s/result' % name

    provider = FormProvider(name, 
                             attribute_mapper=attribute_mapper,
                             host_whitelist=host_whitelist,
                             host_blacklist=host_blacklist,
                             connector_key=connector_key
                            )

    config.add_route(provider.login_route, login_path)
    config.add_view(provider, attr='login', route_name=provider.login_route,
                    permission=NO_PERMISSION_REQUIRED,
                    renderer='velruse:providers/localform/templates/form_login.mako')
    config.add_route(provider.callback_route, result_path,
                     use_global_views=True, factory=provider.result)

    register_provider(config, name, provider)


class FormProvider(object):

    def __init__(self, name, 
                       attribute_mapper=None,
                       host_whitelist=None, 
                       host_blacklist=None,
                       connector_key=None):

        self.name = name
        self.type = 'velruse_form'
        self.login_route = 'velruse.form-%s-login' % self.name
        self.callback_route = 'velruse.form-%s-callback' % self.name
        self.connector_key = connector_key
        self.attribute_mapper = attribute_mapper

    def login(self, request):
        """Show a login form to the user"""
        parms = {}
        parms['endpoint'] = request.POST.get('endpoint', '')
        log.debug('endpoint: %s' % parms['endpoint'] )
        parms['auth_session_key'] = request.POST.get('auth_session_key','')
        parms['form_submitted'] = request.POST.get('form.submitted','')

        if parms['form_submitted'] != request.session.get_csrf_token():
            parms['form_submitted'] = request.session.new_csrf_token()

        parms['login_url'] = request.route_url(self.callback_route)

        return parms

    def result(self, request):
        """Initiate a User login"""
        parms = {}
        parms['endpoint'] = request.POST.get('endpoint', '')
        if parms['endpoint']:
            request.session['endpoint'] = parms['endpoint']
        parms['auth_session_key'] = request.POST.get('auth_session_key','')
        parms['form_submitted'] = request.POST.get('form.submitted','')

        if parms['form_submitted'] != request.session.get_csrf_token():
            return FormAuthFail(provider_name=self.name,
                                provider_type=self.type)

        login = request.POST.get('login', '')
        password = request.POST.get('password', '')

        conn = getattr(request, self.connector_key, None)

        if conn is None:
            raise Exception('auth connector %s not found in request attribute' %
                            self.connector_key)
        userentry = conn.authenticate(login, password)

        if userentry is not None:
            log.debug('user: %s' % userentry[1])
            log.debug('endpoint: %s' % parms['endpoint'])
            profile = self._profile(userentry)
            return FormAuthOK(profile=profile, credentials={},
                              provider_name=self.name,
                              provider_type=self.type)

        log.debug('auth failed')
        return FormAuthFail(provider_name=self.name,
                            provider_type=self.type)

    def _profile(self, userentry):
        log.debug(userentry[1])
        if self.attribute_mapper:
            return self.attribute_mapper(userentry[1])
        return userentry[1]

def _setup_login_forms_from_settings(config):
    settings = config.registry.settings
    forms = aslist(settings.get('velruse.localform.forms', ''))

    for form in forms:
        _setup_form_from_settings(config, name=form)

def _setup_form_from_settings(config, name=''):
    settings = config.registry.settings
    prefix = 'velruse.localform.form.%s.' % name
    p = ProviderSettings(settings, prefix)
    p.update('name')
    p.update('backend')
    p.update('consumers')
    p.update('attribute_mappings')

    _setup_connection_from_settings(config, name=p['backend'])
    _setup_query_from_setting(config, name=p['backend'])

    config.add_form_login(**p.kwargs)

def _setup_backend_from_settings(config, name=''):
    settings = config.registry.settings
    prefix = 'velruse.localform.backend.%s.' % name
    _setup_connection_from_settings(config, prefix)
    _setup_query_from_setting(config, prefix)

def _setup_query_from_setting(config, name=''):

    parm_names = ('formatter', 'filter_tmpl', 'scope', 'cache_period',
                  'search_after_bind', )

    settings = config.registry.settings
    prefix = 'velruse.localform.backend.%s.' % name

    _parms = {}

    settings = config.registry.settings

    for key in parm_names:
        _parms[key] = settings.get('%s.%s'(prefix, key), '').strip()

    _cd_extractor = ConnectionData()

    try:
        data = _cd_extractor.deserialize(_parms)
        data['context'] = name
        logger.debug('data=%r' % data)
        ldap_set_login_query(**data)
    except:
        logger.debug('raw_data=%r' % _parms)


def _setup_connection_from_settings(config, name=''):

    prefix = 'velruse.localform.backend.%s.' % name

    parm_names = ('uri', 'bind', 'passwd', 'pool_size', 'retry_max'
                  'retry_delay', 'use_tls', 'timeout', 'use_pool',)

    _parms = {}

    settings = config.registry.settings

    for key in parm_names:
        _parms[key] = settings.get('%s.%s'(prefix, key), '').strip()

    extractor = ConnectionData()

    try:
        data = extractor.deserialize(_parms)
        data['context'] = name
        logger.debug('data=%r' % data)
        uri = data.pop('uri')
        ldap_setup(config, uri, **data)

    except:
        logger.debug('raw_data=%r' % _parms)


def attach_named_backend(config, cls_setup, *args, **kw):

    connector = cls_setup( *args, **kw)
    name = kw.pop('name', 'backend')

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

def includeme(config):

    config.add_directive('add_form_login', add_form_login)

    if CFG_PREFIX in config.registry.settings['pyramid.includes']:
        _setup_login_forms_from_settings(config)

