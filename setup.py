#!/usr/bin/env python

import sys
from setuptools import setup

setup(
    name='xfork',
    version='0.30',
    description='submitting cpu-bound tasks to processes and io-bound tasks to threads',
    author='Sven R. Kunze',
    author_email='srkunze@mail.de',
    url='https://github.com/srkunze/fork',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],

    py_modules=['fork'],
    install_requires=['futures'] if sys.version_info[0] == 2 else []
)
