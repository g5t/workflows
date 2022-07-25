from skbuild import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

KEYWORDARGS = dict(
    packages=['module'],
    include_package_data=True,
    name='g5t-module',
    author='Greg Tucker',
    author_email='gregory.tucker@ess.eu',
    description='Test Module.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/g5t/workflow",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: C++",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
    ]
)

setup(**KEYWORDARGS)
