
from __future__ import with_statement
import os

from setuptools import setup, find_packages

from mezzanine_wiki import __version__ as version

install_requires = [
    "mezzanine >= 1.1.2",
    "markdown",
    "diff-match-patch",
]

try:
    setup(
        name="mezzanine-wiki",
        version=version,
        author="Dmitry Falk",
        author_email="dfalk5@gmail.com",
        description="Wiki app for Mezzanine content management platform.",
        long_description=open("README.rst").read(),
        license="BSD",
        #url="http://mezzanine.jupo.org/",
        zip_safe=False,
        include_package_data=True,
        packages=find_packages(),
        install_requires=install_requires,
        entry_points="""
            [console_scripts]
        """,
        classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: Web Environment",
            "Framework :: Django",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Internet :: WWW/HTTP",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
            "Topic :: Internet :: WWW/HTTP :: WSGI",
            "Topic :: Software Development :: Libraries :: "
                                                "Application Frameworks",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],)
except:
    pass
