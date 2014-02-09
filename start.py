import socket
import select
import re
import base64
import hashlib
import struct

handshake = '\
HTTP/1.1 101 Web Socket Protocol Handshake\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: %s\r\n\r\n\
'

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER.bind(('', 9999))
SERVER.listen(10)
epoll = select.epoll()
epoll.register(SERVER, select.EPOLLIN)

clients = {}


class ClientConnectionError(Exception): pass
class FrameError(Exception): pass

class Frame:

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
      self.len = (ord(buf[0]) * 1 << 8)
      self.len += ord(buf[1])
      self.frame_length = 8 + self.len
      if self.frame_length > len(self.buf):
        raise FrameError("Incomple Frame: FRAME DATA")
      buf = buf[2:]
      self.key = buf[:4]
      buf = buf[4:4+len(buf)+1]

    else:
      raise FrameError("Inplement payload = 127")
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
        msg += str(chr(o)) + extra_len
      msg += buf
      return msg
    

class Client:

  _poll = epoll

  def __init__(self, sock):
    self.sock = sock
    self.bufferOut = ""
    self.bufferIn = ""
    self.frame_pending = None
    self.commandStack = []
    Client._poll.register(sock, select.EPOLLIN)
    clients[sock.fileno()] = self
    self.handshake = False
    self.key = None
    self.login = "User %s" % len(clients)
    self.channel = "/"

  def recv(self, read_len=1024):
    buf = self.sock.recv(read_len)
    if len(buf) == 0:
      raise ClientConnectionError("Client disconnected.")
      return ""
    self.bufferIn += buf
    return self.bufferIn

  def send(self, cmd):
    try:
      self.bufferOut += cmd
      Client._poll.modify(self.sock, select.EPOLLIN | select.EPOLLOUT)
    except Exception, e:
      raise ClientConnectionError("Epoll error")
      

  def consume(self):
    try:
      ret = self.sock.send(self.bufferOut)
      if ret < 0:
        raise ClientConnectionError("Disconnected")
      self.bufferOut = self.bufferOut[ret:]
      if len(self.bufferOut) == 0:
        Client._poll.modify(self.sock, select.EPOLLIN)
    except Exception, e:
      print e
      

  def initHandcheck(self):
    buf = self.recv()
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
    self.send(handshake % key)
    self.handshake = True


  def onReceive(self):
    if self.handshake == False:
      self.initHandcheck()
      return
    try:
      buf = self.recv()
      f = Frame(buf)
      msg = f.getMsg()
      f_len = f.getFrameLenght()
      self.bufferIn = buf[f_len:]
      for fileno, c in clients.items():
        c.send(Frame.buildMsg(msg))
    except FrameError, e:
      print str(e)

def registerClient():
  new_client , addr = SERVER.accept()
  Client(new_client)

while True:
  events = epoll.poll()
  for fileno, event in events:

    try:
      if event & select.EPOLLIN:
        if fileno == SERVER.fileno():
          registerClient()
        else:
          clients[fileno].onReceive()
      if event & select.EPOLLOUT:
        clients[fileno].consume()
      if event == select.EPOLLHUP:
        print "diconnect"
        pass

    except ClientConnectionError, e:
      c = clients[fileno]
      Client._poll.unregister(c.sock)
      try:
        c.sock.close()
      except:
        pass
      del clients[fileno]
    except Exception, e:
      c = clients[fileno]
      Client._poll.unregister(c.sock)
      try:
        c.sock.close()
      except:
        pass
      del clients[fileno]

