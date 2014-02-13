import unittest
import WebsocketTwisted

class FrameTest(unittest.TestCase):

  def setUp(self):
    pass

def test_Frame__init__(self):
  try:
    f = WebsocketTwisted.server.Frame("")
    self.assertTrue(False,"Frame with empty buffer")
  except:
    self.assertTrue(False)


if __name__ == '__main__':
  unittest.main()