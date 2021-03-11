# -*- coding: utf-8 -*-
#
# you can install this to a local test virtualenv like so:
#   virtualenv venv
#   ./venv/bin/pip install --editable .
#   ./venv/bin/pip install --editable .[dev]  # with dev requirements, too

import rsvis

import glob
import setuptools
import sys

with open("README.md") as fd:
    long_description = fd.read()

if sys.platform == "win32":
    data_files = []
else:
    data_files = []

included_packages = ["rsvis"] + ["rsvis." + p for p in setuptools.find_packages("rsvis")]

setuptools.setup(
    name="rsvis",
    version=rsvis.__version__,
    maintainer=rsvis.__maintainer__,
    maintainer_email=rsvis.__email__,
    author=rsvis.__author__,
    author_email=rsvis.__email__,
    license=rsvis.__license__,
    url="https://github.com/wbrandenburger/DataVisualization",
    install_requires=[
        # - python project packages - 
        "colorama>=0.4.3",
        "click>=7.1.2",
        "stevedore>=1.32.0",
        "configparser>=5.0.0",
        "pyyaml>=5.3.1",
        "natsort>=7.0.0",
        "pandas==1.2.3",
        "seaborn==0.11.1",
        "tqdm == 4.58.0",
        "json5 == 0.9.5",
        # - python image processing packages -
        "opencv-contrib-python==4.5.1.48",
        # "opencv-contrib-python>=4.2.0.34",        
        "Pillow==8.1.1",
        "tifffile>=2020.2.16",
        "scikit-image==0.18.1",
        # - python numerical analysis packages -
        "matplotlib==3.3.4",
        "scikit-learn==0.24.1"
    ],
    python_requires=">=3",
    classifiers=[
        "Development Status :: 1 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
    ],
    extras_require=dict(
        # List additional groups of dependencies here (e.g. development
        # dependencies). You can install these using the following syntax,
        # for example:
        # $ pip install -e .[develop]
        optional=[
        ],
        develop=[
        ]
    ),
    description=(
        "Visualization tool for exploring and for viewing remote sensing data."
    ),
    long_description=long_description,
    keywords=[
        "visualization", "remote sensing", "images", "aerial", "satellite", "viewer", "explorer", "science", "research", "command-line", "tui"
    ],
    package_data=dict(
        rsvis=[
        ],
    ),
    data_files=data_files,
    packages=included_packages,
    entry_points={
        "console_scripts": [
            "rsvis=rsvis.commands.default:run",
        ],
        "rsvis.command": [
            "run=rsvis.commands.run:cli"
        ],
    },
    platforms=["linux", "osx", "windows"],
)
