import os

from setuptools import setup, find_packages

readme_file = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(readme_file).read()

classifiers = [
    'Development Status :: 5 - Beta',
    'Framework :: Django',
    'License :: OSI Approved :: MIT License']

setup(name='django-crowdsourcing',
      version='2.1.0',
      include_package_data=True,
      classifiers=classifiers,
      description='Django app for collecting and displaying surveys.',
      long_description=long_description,
      author='Jacob Smullyan, Dave Smith',
      author_email='jsmullyan@gmail.com',
      url='http://code.google.com/p/django-crowdsourcing/',
      packages=find_packages(exclude=('example_app*',)),
      license='MIT',
      )
