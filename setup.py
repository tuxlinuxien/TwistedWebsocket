import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "TwistedWebsoket",
    version = "0.0.1",
    author = "Yoann Cerda",
    author_email = "tuxlinuxien@gmail.com",
    description = (""),
    license = "BSD",
    keywords = "websocket server",
    url = "https://github.com/tuxlinuxien/TwistedWebsocket",
    packages=['TwistedWebsocket'],
    install_requires = ['twisted'],
    long_description=read('README.md'),
)
