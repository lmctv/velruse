import requests
from pyramid.config import Configurator
from pyramid.view import view_config
from logging import getLogger

log = getLogger(__name__)

@view_config(route_name='login', renderer='sample_localform_app:templates/login.mako')
def login(request):
    return {}


@view_config(route_name='logged_in', renderer='json')
def logged_in(request):
    token = request.POST['token']
    log.debug(request.POST)
    payload = {'format': 'json', 'token': token}
    response = requests.get('http://localhost:8521/auth_info', params=payload)
    log.debug(response)

    return {'result': response.json()}


def main(global_config, **settings):
    '''Main config function'''
    config = Configurator(settings=settings)
    config.include('pyramid_debugtoolbar')
    config.add_route('login', '/login')
    config.add_route('logged_in', '/logged_in')
    config.scan('.')
    return config.make_wsgi_app()
