#!/usr/bin/env python2.7
# coding: utf-8

"""_
# Mdv installation

## Usage

    [sudo] ./setup.py install

----
"""


from setuptools import setup, find_packages
version = '1.5.0'

setup(
    name='mdv',
    version=version,
    packages=find_packages(),
    author="Axiros GmbH",
    author_email="gk@axiros.com",
    description="Terminal Markdown Viewer",
    long_description=open('README.md').read(),
    install_requires=["pyyaml", "pygments", "markdown", "docopt"],
    include_package_data=True,
    url='http://github.com/axiros/terminal_markdown_viewer',
    download_url='http://github.com/axiros/terminal_markdown_viewer/tarball/' + version,
    keywords = ['markdown', 'markup', 'terminal', 'hilighting', 'syntax', 'source code'],
    classifiers=[
        "Programming Language :: Python",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Topic :: Text Processing :: Markup",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7",
    ],
    entry_points = {
        'console_scripts': [
            'mdv = mdv:run',
        ],
    },
)
