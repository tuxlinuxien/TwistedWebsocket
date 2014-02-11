import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "TwistedWebsocket",
    version = "0.0.3",
    author = "Yoann Cerda",
    author_email = "tuxlinuxien@gmail.com",
    description = ("Websocket protocol implementation based on Twisted"),
    license = "MIT",
    keywords = "websocket server twisted",
    url = "https://github.com/tuxlinuxien/TwistedWebsocket",
    packages=['TwistedWebsocket'],
    install_requires = ['twisted'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
    ],
)
