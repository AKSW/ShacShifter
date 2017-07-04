#!/usr/bin/env python

from distutils.core import setup

setup(
    name='ShacShifter',
    version='0.1',
    description='A tool to transfom Saape Expressions into something other',
    author='Natanael Arndt, Norman Radtke',
    author_email='arndt@informatik.uni-leipzig.de, radtke@informatik.uni-leipzig.de',
    license='GNU General Public License Version 3',
    url='https://github.com/AKSW/ShacShifter',
    download_url='https://github.com/AKSW/ShacShifter/archive/master.tar.gz',
    install_requires=[
        'rdflib==4.2.1'
    ],
    dependency_links=[
        'rdflib==4.2.1'
    ],
    packages=[
        'ShacShifter'
    ]
)
