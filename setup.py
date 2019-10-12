from os.path import join, dirname
from setuptools import setup, find_packages
try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    from pip.req import parse_requirements

def load_requirements(fname):
    reqs = parse_requirements(fname, session="test")
    return [str(ir.req) for ir in reqs]


PACKAGE = find_packages()
NAME = "django_autocompleter"
DESCRIPTION = ""
AUTHOR = "Stas Shilov"
AUTHOR_EMAIL = "shilowstanisalw@gamail.com"
URL = "https://github.com/stanley0707/django_autocompleter.git"
VERSION = "0.0.1"
 
setup(
    name=NAME,
    install_requires=load_requirements("requirements.txt"),
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