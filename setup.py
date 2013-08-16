"""
Playing politics setup.
"""

from setuptools import setup, find_packages

setup( name='arcade',
       version='0.1',
       description='Loft app for multiplayer games.',
       author='Matt Easterday',
       author_email='easterday@northwestern.edu',
       packages = find_packages(),
       include_package_data = True,
       zip_safe = False,
       install_requires = ['gevent-socketio', 'jsonfield']
      )