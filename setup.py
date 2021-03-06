#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


readme = open('README.md').read()
history = open('HISTORY.md').read().replace('.. :changelog:', '')

requirements = [
    'requests',
    'future',
    'django',
]

test_requirements = [
    'mock',
    'nose',
    'nose-parameterized',
]

setup(
    name='django-dispatcher',
    version='0.4.8',
    description='Django logic engine (used for email logic)',
    long_description=readme + '\n\n' + history,
    author='G Adventures',
    author_email='software@gadventures.com',
    url='https://github.com/gadventures/django-dispatcher',
    packages=find_packages(),
    package_dir={'dspatcher': 'dispatcher'},
    include_package_data=True,
    install_requires=requirements,
    license='MIT',
    zip_safe=False,
    keywords='dispatcher',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='nose.collector',
    tests_require=test_requirements,
)
