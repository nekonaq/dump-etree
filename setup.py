# -*- coding: utf-8 -*-
from setuptools import setup


def get_version(fname='dump_etree.py'):
    with open(fname) as fp:
        for line in fp:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])

setup(
    name='dump_etree',
    version=get_version(),
    description="dump tree structure of html",
    author="Tatsuo Nakajyo",
    author_email="tnak@nekonaq.com",
    license='BSD',
    py_modules=['dump_etree'],
    entry_points={
        'console_scripts': [
            'dump-etree = dump_etree:Command.main',
            ]
        },
    install_requires=['lxml'],
    )
