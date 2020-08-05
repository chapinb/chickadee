"""Installer for chickadee"""
import setuptools
from libchickadee import __version__, __desc__, __author__

with open('README.md') as fh:
    long_description = fh.read()

setuptools.setup(
    name='chickadee',
    version=__version__,
    description=__desc__,
    author=__author__,
    author_email='python@chapinb.com',
    url='https://github.com/chapinb/chickadee',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'chickadee = libchickadee.chickadee:entry'
        ]
    },
    install_requires=[
        "requests ~= 2.22.0",
        "openpyxl ~= 2.6.3",
        "tqdm ~= 4.36.1",
        "netaddr ~= 0.7.19",
        "python-evtx ~= 0.6.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Telecommunications Industry",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Other Audience",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Security",
        "Topic :: Utilities"
    ]
)
