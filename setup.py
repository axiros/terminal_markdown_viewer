#!/usr/bin/env python2.7
# coding: utf-8

"""_
# Mdv installation

## Usage

    [sudo] ./setup.py install

----
"""

import os
from setuptools import setup, find_packages

version = "2.0.1"

with open(os.path.join(os.path.dirname(__file__), "README.md")) as fd:
    md = fd.read()

with open('requirements.txt', 'r') as f:
    install_requires = f.read().replace(' ', '').split('\n')

# images hack for pypi:
gh = 'https://raw.githubusercontent.com/WillNye/terminal_markdown_viewer/master'
md = md.replace('src="./', 'src="%s/' % gh)

setup(
    name="mdv3",
    version=version,
    packages=find_packages(),
    author="Will Beasley",
    author_email='willbeas88@gmail.com',
    description="Terminal Markdown Viewer",
    python_requires='>=3.7',
    install_requires=install_requires,
    extras_require={"yaml": "pyyaml"},
    long_description=md,
    long_description_content_type="text/markdown",
    include_package_data=True,
    url="http://github.com/WillNye/terminal_markdown_viewer",
    download_url="http://github.com/WillNye/terminal_markdown_viewer/tarball/",
    keywords=[
        "markdown",
        "markup",
        "terminal",
        "hilighting",
        "syntax",
        "source code",
    ],
    test_suite="nose.collector",
    tests_require=["nose"],
    classifiers=[
        "Programming Language :: Python",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Topic :: Text Processing :: Markup",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={"console_scripts": ["mdv = mdv:run"]},
)
