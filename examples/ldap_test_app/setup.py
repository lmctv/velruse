from setuptools import setup, find_packages

requires = [
    'velruse',
    'pyramid',
    'pyramid_ldap>=0.2.dev',
    'waitress',
    'redis',
    'pyramid_debugtoolbar',
    'requests',
]

setup(name='sample_ldapapp',
      version='0.0-dev',
      description='Velruse example provider application',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = sample_ldapapp:main
      """,
)
