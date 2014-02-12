class FrameError(Exception): pass

class ServerFrame(object):

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
      raise FrameError("Incomple Frame: HEADER DATA")
    self.fin = ord(buf[0]) >> 7
    self.opcode = ord(buf[0]) & 0b1111
    self.payload = ord(buf[1]) & 0b1111111
    buf = buf[2:]
    if self.payload < 126:
      self.len = self.payload
      self.frame_length = 6 + self.len
      if self.frame_length > len(self.buf):
        raise FrameError("Incomple Frame: FRAME DATA")

      if len(buf) < 4:
        raise FrameError("Incomple Frame: KEY DATA")
      self.key = buf[:4]
      buf = buf[4:4+len(buf)+1]

    elif self.payload == 126:
      if len(buf) < 6:
        raise FrameError("Incomple Frame: KEY DATA")
      for k,i in [(0,1),(1,0)]:
        self.len += (ord(buf[k]) * 1 << (8*i))
      self.frame_length = 8 + self.len
      if self.frame_length > len(self.buf):
        raise FrameError("Incomple Frame: FRAME DATA")
      buf = buf[2:]
      self.key = buf[:4]
      buf = buf[4:4+len(buf)+1]

    else:
      if len(buf) < 10:
        raise FrameError("Incomple Frame: KEY DATA")
      for k,i in [(0,7),(1,6),(2,5),(3,4),(4,3),(5,2),(6,1),(7,0)]:
        self.len += (ord(buf[k]) * 1 << (8*i))
      self.frame_length = 14 + self.len
      if self.frame_length > len(self.buf):
        raise FrameError("Incomple Frame: FRAME DATA")
      buf = buf[8:]
      self.key = buf[:4]
      buf = buf[4:4+len(buf)+1]
    self.msg = buf

  def message(self):
    self.isReady()
    decoded_msg = ""
    for i in xrange(self.len):
      c = ord(self.msg[i]) ^ ord(self.key[i % 4])
      decoded_msg += str(chr(c))
    return decoded_msg

  def lenght(self):
    return self.frame_length

  @staticmethod
  def buildMessage(buf):
    c_buf = buf
    msg = ""
    #first byte
    o = (1 << 7) + 1
    msg += str(chr(o))
    #second byte
    buf_len = len(buf)
    if buf_len < 126:
      o = buf_len
      msg += str(chr(o))
      msg += buf
      return msg

    if buf_len <= ((1 << 16) - 1):
      msg += str(chr(126))
      for i in range(1,3):
        o = (buf_len >> (16 - (8*i))) & (2**8 - 1)
        msg += str(chr(o))
      msg += buf
      return msg

    if buf_len <= ((1 << 64) - 1):
      msg += str(chr(127))
      for i in range(1,9):
        o = (buf_len >> (64 - (8*i))) & (2**8 - 1)
        msg += str(chr(o))
      msg += buf
      return msg