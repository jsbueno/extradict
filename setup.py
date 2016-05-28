# coding: utf-8

from setuptools import setup

setup(
    name = 'extradict',
    packages = ['extradict'],
    version = "0.1.9",
    license = "LGPLv3+",
    author = "João S. O. Bueno",
    author_email = "gwidion@gmail.com",
    description = "Enhanced, maybe useful, data containers. For now, a versioned dict and an ordered versioned dict",
    keywords = "versioned transactional container collection dict dictionary",
    py_modules = ['extradict'],
    url = 'https://github.com/jsbueno/extradict',
    long_description = open('README.md').read(),
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: PyPy",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ]
)
