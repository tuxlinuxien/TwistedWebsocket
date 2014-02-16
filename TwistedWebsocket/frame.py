import random
from exception import FrameError

class Frame(object):

  def __init__(self, buf):
    self.buf = buf
    self.msg = ""
    self.mask = 0
    self.key = ""
    self.len = 0
    self.fin = 0
    self.payload = 0
    self.opcode = 0
    self.frame_length = 0
    self.isReady()

  def isReady(self):
    buf = self.buf
    if len(buf) < 2:
      raise FrameError("Incomplet Frame: HEADER DATA")
    self.fin = ord(buf[0]) >> 7
    self.opcode = ord(buf[0]) & 0b1111
    self.payload = ord(buf[1]) & 0b1111111
    self.mask = ord(buf[1]) >> 7
    buf = buf[2:]
    if self.payload < 126:
      self.len = self.payload
      if self.mask:
        self.frame_length = 6 + self.len
      else:
        self.frame_length = 2 + self.len
      if self.frame_length > len(self.buf):
        raise FrameError("Incomplet Frame: FRAME DATA")
      if len(buf) < 4 and self.mask:
        raise FrameError("Incomplet Frame: KEY DATA")
      if  self.mask:
        self.key = buf[:4]
        buf = buf[4:4+len(buf)+1]
      else:
        buf = buf[:self.len]

    elif self.payload == 126:
      if len(buf) < 6 and self.mask:
        raise FrameError("Incomplet Frame: KEY DATA")
      for k,i in [(0,1),(1,0)]:
        self.len += (ord(buf[k]) * 1 << (8*i))
      if self.mask:
        self.frame_length = 8 + self.len
      else:
        self.frame_length = 4 + self.len
      if self.frame_length > len(self.buf):
        raise FrameError("Incomplet Frame: FRAME DATA")
      buf = buf[2:]
      if self.mask:
        self.key = buf[:4]
        buf = buf[4:4+len(buf)+1]
      else:
        buf = buf[:self.len]

    else:
      if len(buf) < 10 and self.mask:
        raise FrameError("Incomplet Frame: KEY DATA")
      for k,i in [(0,7),(1,6),(2,5),(3,4),(4,3),(5,2),(6,1),(7,0)]:
        self.len += (ord(buf[k]) * 1 << (8*i))
      if self.mask:
        self.frame_length = 14 + self.len
      else:
        self.frame_length = 10 + self.len
      if self.frame_length > len(self.buf):
        raise FrameError("Incomplet Frame: FRAME DATA")
      buf = buf[8:]
      if self.mask:
        self.key = buf[:4]
        buf = buf[4:4+len(buf)+1]
      else:
        buf = buf[self.len]
    self.msg = buf

  def message(self):
    if not self.mask:
      return self.msg
    decoded_msg = ""
    for i in xrange(self.len):
      c = ord(self.msg[i]) ^ ord(self.key[i % 4])
      decoded_msg += str(chr(c))
    return decoded_msg

  def length(self):
    return self.frame_length

  @staticmethod
  def encodeMessage(buf, key):
    encoded_msg = ""
    buf_len = len(buf)
    for i in xrange(buf_len):
      c = ord(buf[i]) ^ ord(key[i % 4])
      encoded_msg += str(chr(c))
    return encoded_msg

  @staticmethod
  def buildMessage(buf, mask=True):
    c_buf = buf
    msg = ""
    if mask:
      key = "".join([str(chr(random.randrange(1,255))) for i in xrange(4)])
    #first byte
    o = (1 << 7) + 1
    msg += str(chr(o))
    #second byte
    buf_len = len(buf)
    if buf_len < 126:
      o = buf_len
      if mask:
        msg += str(chr(o + (1<<7)))
      else:
        msg += str(chr(o))
      if mask:
        msg += key
        msg += Frame.encodeMessage(buf,key)
      else:
        msg += buf
      return msg

    if buf_len <= ((1 << 16) - 1):
      if mask:
        msg += str(chr(126 + (1<<7)))
      else:
        msg += str(chr(126))
      for i in range(1,3):
        o = (buf_len >> (16 - (8*i))) & (2**8 - 1)
        msg += str(chr(o))
      if mask:
        msg += key
        msg += Frame.encodeMessage(buf,key)
      else:
        msg += buf
      return msg

    if buf_len <= ((1 << 64) - 1):
      if mask:
        msg += str(chr(127 + (1<<7)))
      else:
        msg += str(chr(127))
      for i in range(1,9):
        o = (buf_len >> (64 - (8*i))) & (2**8 - 1)
        msg += str(chr(o))
      if mask:
        msg += key
        msg += Frame.encodeMessage(buf,key)
      else:
        msg += buf
      return msg