import uuid
import re
import hashlib
import base64
from twisted.internet.protocol import Protocol as BaseProtocol

handshake = '\
HTTP/1.1 101 Web Socket Protocol Handshake\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: %s\r\n\r\n\
'

class WebSocketError(Exception): pass
class FrameError(Exception): pass

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

  def _frameHeader(self):
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

  def getMsg(self):
    self._frameHeader()
    decoded_msg = ""
    for i in xrange(self.len):
      c = ord(self.msg[i]) ^ ord(self.key[i % 4])
      decoded_msg += str(chr(c))
    return decoded_msg

  def getFrameLenght(self):
    return self.frame_length

  @staticmethod
  def buildMsg(buf):
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


class Protocol(BaseProtocol, object):

  def __init__(self, users):
    self.bufferIn = ""
    self.users = users
    self.id = str(uuid.uuid4())
    self.users[self.id] = self
    self.websocket_ready = False
    self.commands = []

  def sendHandcheck(self):
    buf = self.bufferIn
    pos = buf.find("\r\n\r\n")
    if pos == -1:
      return
    cmd = buf[:pos+5]
    self.bufferIn = buf[pos+4:]
    key = re.search("Sec-WebSocket-Key:\s*(\S+)\s*", cmd)
    key = key.group(1)
    self.key = key
    key = key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    key = base64.b64encode(hashlib.sha1(key).digest())
    self.transport.write(handshake % key)
    self.websocket_ready = True

  def dataReceived(self, data):
    self.bufferIn += data
    if not self.websocket_ready:
      self.sendHandcheck()
      self.onConnect()
    else:
      try:
        f = Frame(self.bufferIn)
        msg = f.getMsg()
      except FrameError, e:
        pass
      else:
        f_len = f.getFrameLenght()
        self.bufferIn = self.bufferIn[f_len:]
        self.onMessage(msg)

  def connectionLost(self, *args, **kwargs):
    _id = self.id
    if self.id in self.users:
      del self.users[self.id]
    self.onDisconnect()

  def loseConnection(self):
    _id = self.id
    if self.id in self.users:
      del self.users[self.id]
    self.onDisconnect()
    self.transport.loseConnection()

  def abortConnection(self):
    _id = self.id
    if self.id in self.users:
      del self.users[self.id]
    self.onDisconnect()
    self.transport.abortConnection()

  def onConnect(self):
    pass

  def onDisconnect(self):
    pass

  def onMessage(self, msg):
    pass

  def sendMessage(self, msg):
    self.commands.append(msg)
    if not self.websocket_ready:
      return
    for cmd in self.commands:
      self.transport.write(Frame.buildMsg(cmd))
    self.commands = []