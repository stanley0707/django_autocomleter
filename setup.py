from os.path import join, dirname
from setuptools import setup, find_packages

PACKAGE = find_packages()
NAME = "django_autocompleter"
DESCRIPTION = ""
AUTHOR = "Stas Shilov"
AUTHOR_EMAIL = "shilowstanisalw@gamail.com"
URL = "https://github.com/stanley0707/django_autocompleter.git"
VERSION = "0.0.1"
 
setup(
    name=NAME,
    install_requires=open(join(dirname(__file__), 'requirements.txt')).read(),
    version=VERSION,
    description=DESCRIPTION,
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=PACKAGE,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
)