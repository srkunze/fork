#!/usr/bin/env python

from distutils.core import setup

setup(
    name='xfork',
    version='0.2',
    description='submitting cpu-bound tasks to processes and io-bound tasks to threads',
    author='Sven R. Kunze',
    author_email='srkunze@mail.de',
    py_modules=['fork'],
)
