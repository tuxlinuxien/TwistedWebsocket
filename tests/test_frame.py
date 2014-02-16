#!/usr/bin/env python

import unittest
from TwistedWebsocket.server import Frame, FrameError, Protocol, ProtocolError

def client_frame_builder(times, encrypt=True):
  frame_buf = ""
  o = 1 << 7
  o += 1
  frame_buf += chr(o)
  if times < 126:
    if encrypt:
      frame_buf += chr(times + (1 << 7))
    else:
      frame_buf += chr(times)
  elif times <= ((1 << 16) - 1):
    if encrypt:
      frame_buf += chr(126 + (1<<7))
    else:
      frame_buf += chr(126)
    frame_buf += chr(times >> 8)
    frame_buf += chr(times & (2**8 - 1))
  elif times <= ((1 << 64) - 1):
    if encrypt:
      frame_buf += chr(127 + (1<<7))
    else:
      frame_buf += chr(127)
    for i in [7,6,5,4,3,2,1,0]:
      o = times >> (8*i)
      frame_buf += chr(o & (2**8 - 1))
  key = "1234"
  if encrypt:
    frame_buf += key
    msg = ""
    for i in xrange(times):
      c = ord('a') ^ ord(key[i % 4])
      msg += str(chr(c))
    frame_buf += msg
  else:
    msg = "a"*times
    frame_buf += msg
  return frame_buf


class TestingInit(unittest.TestCase):
  
  def setUp(self):
    self.clients = {}
    self.handler = Protocol(self.clients)


class ServerFrameTest(TestingInit):

  """
  Server Frame Testing
  """
  def test_Frame__init__(self):
    frame_data = client_frame_builder(10)
    Frame(frame_data)

  def test_Frame__init__error(self):
    self.assertRaises(FrameError, Frame, "")

  def build_test_Frame_message(self, msg_len):
    msg = ""
    try:
      frame_data = client_frame_builder(msg_len)
      f = Frame(frame_data)
      msg = f.message()
    except Exception, e:
      print e
    finally:
      self.assertEqual(msg, "a"*msg_len, "Error decode %s length message" % msg_len)

  def test_Frame_message(self):
    self.build_test_Frame_message(0)
    self.build_test_Frame_message(10)
    self.build_test_Frame_message(125)
    self.build_test_Frame_message((1 << 16) - 1)
    self.build_test_Frame_message(1 << 16)
    self.build_test_Frame_message(2**8 - 1)

  def build_test_Frame_buildMessage(self, msg_len):
    msg = ""
    try:
      frame_data = client_frame_builder(msg_len, encrypt=False)
      msg = Frame.buildMessage("a"*msg_len, mask=False)
    except Exception, e:
      print e
    finally:
      self.assertEqual(frame_data, msg, "Error decode %s length message" % msg_len)

  def test_Frame_buildMessage(self):
    self.build_test_Frame_buildMessage(10)
    self.build_test_Frame_buildMessage(125)
    self.build_test_Frame_buildMessage(126)
    self.build_test_Frame_buildMessage((1 << 16) - 1)
    self.build_test_Frame_buildMessage(1 << 16)
    self.build_test_Frame_buildMessage(2**8 - 1)

  def test_Frame_length(self):
    frame_data = client_frame_builder(100)
    f = Frame(frame_data)
    self.assertEqual(f.length(), len(frame_data))


  def build_test_Frame_buildMessage_to_client(self, msg_len):
    msg = ""
    try:
      frame_data = client_frame_builder(msg_len, encrypt=True)
      msg = Frame.buildMessage("a"*msg_len, mask=True)
      frame_data = Frame(frame_data)
      msg = Frame(msg)
    except Exception, e:
      print e
    finally:
      self.assertEqual(frame_data.message(), msg.message(), "Error decode %s length message" % msg_len)

  def test_Frame_buildMessage_to_client(self):
    self.build_test_Frame_buildMessage_to_client(10)
    self.build_test_Frame_buildMessage_to_client(125)
    self.build_test_Frame_buildMessage_to_client(126)
    self.build_test_Frame_buildMessage_to_client((1 << 16) - 1)
    self.build_test_Frame_buildMessage_to_client(1 << 16)
    self.build_test_Frame_buildMessage_to_client(2**8 - 1)



class ServerProtocolTest(TestingInit):

  client_handcheck = 'GET / HTTP/1.1\r\n\
Upgrade: websocket\r\n\
Connection: Upgrade\r\n\
Host: 127.0.0.1:9999\r\n\
Origin: http://localhost:8000\r\n\
Pragma: no-cache\r\n\
Cache-Control: no-cache\r\n\
Sec-WebSocket-Key: JTD8Ek+1+nPW2alOHOHe8g==\r\n\
Sec-WebSocket-Version: 13\r\n\
Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits, x-webkit-deflate-frame\r\n\
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36\r\n\
\r\n'

  client_handcheck_no_key = 'GET / HTTP/1.1\r\n\
Upgrade: websocket\r\n\
Connection: Upgrade\r\n\
Host: 127.0.0.1:9999\r\n\
Origin: http://localhost:8000\r\n\
Pragma: no-cache\r\n\
Cache-Control: no-cache\r\n\
Sec-WebSocket-Version: 13\r\n\
Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits, x-webkit-deflate-frame\r\n\
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36\r\n\
\r\n'

  def test_isBufferInComsumed(self):
    self.assertEqual(len(self.handler.bufferIn), 0)
  
  def test_Protocol_buildHandcheck_error(self):
    with self.assertRaises(ProtocolError):
      self.handler.buildHandcheck()

  def test_Protocol_buildHandcheck_error_no_key(self):
    self.handler.bufferIn = ServerProtocolTest.client_handcheck_no_key
    with self.assertRaises(Exception):
      self.handler.buildHandcheck()

  def test_Protocol_buildHandcheck_error_no_key(self):
    self.handler.bufferIn = ServerProtocolTest.client_handcheck
    self.handler.buildHandcheck()
    self.test_isBufferInComsumed()

  def test_Protocol_dataReceived(self):
    pass



if __name__ == '__main__':
  unittest.main()