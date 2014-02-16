import uuid
import re
import hashlib
import base64
from twisted.internet.protocol import Protocol as BaseProtocol
from exception import FrameError, ProtocolError
from frame import Frame
import random


handshake = '\
HTTP/1.1 101 Web Socket Protocol Handshake\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: %s\r\n\r\n\
'

#
# Server protocol
#

class Protocol(BaseProtocol, object):

  def __init__(self, users={}):
    self.bufferIn = ""
    self.bufferOut = ""
    self.users = users
    self.id = str(uuid.uuid4())
    self.users[self.id] = self
    self.websocket_ready = False

  def buildHandcheck(self):
    buf = self.bufferIn
    pos = buf.find("\r\n\r\n")
    if pos == -1:
      raise ProtocolError("Incomplet Handshake")
    cmd = buf[:pos+5]
    self.bufferIn = buf[pos+4:]
    key = re.search("Sec-WebSocket-Key:\s*(\S+)\s*", cmd)
    if not key:
      raise Exception("Missing Key")
    key = key.group(1)
    self.key = key
    key = key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    key = base64.b64encode(hashlib.sha1(key).digest())
    return handshake % key


  def sendHandcheck(self):
    try:
      hc = self.buildHandcheck()
    except ProtocolError:
      pass
    except Exception:
        self.transport.abortConnection()
    else:
      self.transport.write(hc)
      self.websocket_ready = True

  def dataReceived(self, data):
    self.bufferIn += data
    if not self.websocket_ready:
      self.sendHandcheck()
      self.onConnect()
    else:
      try:
        frame = Frame(self.bufferIn)
      except FrameError, e:
        pass
      else:
        f_len = frame.length()
        self.bufferIn = self.bufferIn[f_len:]
        self.onMessage(frame.message())

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

  def sendMessage(self, msg):
    self.bufferOut += Frame.buildMessage(msg, mask=False)
    if not self.websocket_ready:
      return
    self.transport.write(self.bufferOut)
    self.bufferOut = ""

  def onConnect(self):
    pass

  def onDisconnect(self):
    pass

  def onMessage(self, msg):
    pass
