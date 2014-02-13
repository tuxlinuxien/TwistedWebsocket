import os
from setuptools import setup
from distutils.cmd import Command

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

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
  version = "0.0.5.1",
  author = "Yoann Cerda",
  maintainer = "Yoann Cerda",
  author_email = "tuxlinuxien@gmail.com",
  description = ("Websocket protocol implementation based on Twisted"),
  license = "MIT",
  keywords = "websocket server twisted",
  url = "https://github.com/tuxlinuxien/TwistedWebsocket",
  packages=['TwistedWebsocket'],
  install_requires = ['twisted'],
  long_description=read('README.md'),
  test_suite='tests',
  classifiers=[
      "Development Status :: 2 - Pre-Alpha",
      "Environment :: Console",
      "Framework :: Twisted",
      "Intended Audience :: Developers",
      "License :: MIT License",
    ],
  cmdclass = {'test': TestCommand},
)
