#!/usr/bin/env python

from distutils.core import setup

setup(
    name='xfork',
    version='0.5',
    description='submitting cpu-bound tasks to processes and io-bound tasks to threads',
    author='Sven R. Kunze',
    author_email='srkunze@mail.de',
    url='https://github.com/srkunze/fork',
    py_modules=['fork'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)
