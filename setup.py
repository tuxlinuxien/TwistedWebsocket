import os
from setuptools import setup
from distutils.cmd import Command
import TwistedWebsocket.server

class TestCommand(Command):
  user_options = []

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def run(self):
    import sys, subprocess
    raise SystemExit(subprocess.call([sys.executable,'-m','unittest','tests.test_frame']))

setup(
  name = "TwistedWebsocket",
  version = TwistedWebsocket.server.__VERSION__,
  author = "Yoann Cerda",
  maintainer = "Yoann Cerda",
  author_email = "tuxlinuxien@gmail.com",
  description = (TwistedWebsocket.server.__DESCRIPTION__),
  license = "MIT",
  keywords = "websocket server twisted ssl",
  url = "https://github.com/tuxlinuxien/TwistedWebsocket",
  packages=['TwistedWebsocket'],
  install_requires = ['twisted'],
  long_description=open('README.txt').read(),
  test_suite='tests',
  classifiers=[
      "Development Status :: 2 - Pre-Alpha",
      "Environment :: Console",
      "Framework :: Twisted",
      "Intended Audience :: Developers",
    ],
  cmdclass = {'test': TestCommand},
)
