# coding: utf-8

from setuptools import setup
from extradict import __author__, __version__


def get_str_in_line(line):
    quotechar = "'" if "'" in line else "\""
    return line.split(quotechar)[-2]

with open("extradict/__init__.py") as f:
    for line in f:
        if "__author__" in line:
            __author__ = get_str_in_line(line)
        elif "__version__" in line:
            __version__ = get_str_in_line(line)


setup(
    name = 'extradict',
    version = __version__,
    license = "LGPLv3+",
    author = __author__,
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
