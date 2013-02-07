from setuptools import setup, find_packages

requires = [
    'velruse[ldap]',
    'waitress',
    'pyramid_debugtoolbar',
    'requests',
]

setup(name='local_form_test_app',
      version='0.0-dev',
      description='Velruse example provider application',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = sample_localform_app:main
      """,
)
