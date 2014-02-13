#!/usr/bin/env python

import unittest
from TwistedWebsocket.server import Frame, FrameError

class FrameTest(unittest.TestCase):

  def setUp(self):
    pass

  def test_Frame__init__(self):
    self.assertRaises(FrameError, Frame, "")


if __name__ == '__main__':
  unittest.main()