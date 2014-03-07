#!/usr/bin/env python

import uuid
import re
import hashlib
import base64
from twisted.internet.protocol import Protocol as BaseProtocol
from exception import FrameError, ProtocolError
from frame import Frame
import random


#
# Package info
#
__VERSION__ = "0.0.7"
__DESCRIPTION__ = "Websocket server implementation based on Twisted with SSL support."


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
    self.onHandshake(buf)
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

  def onHandshake(self, header):
    pass

  def onConnect(self):
    pass

  def onDisconnect(self):
    pass

  def onMessage(self, msg):
    pass


if __name__ == "__main__":
  from twisted.internet.protocol import Factory
  from twisted.internet import reactor, ssl
  import sys
  import argparse

  class WebSocketHandler(Protocol):

    def onHandshake(self, header):
      g = re.search('Origin\s*:\s*(\S+)', header)
      if not g: return
      print "\n[HANDSHAKE] %s origin : %s" % (self.id, g.group(1))

    def onConnect(self):
      print "\n[CONNECTION] %s connected" % self.id
      for _id, user in self.users.items():
        user.sendMessage("%s connected" % self.id)
        print "\n[FRAME] from %s to %s:\n%s connected" % (self.id, _id, self.id)

    def onDisconnect(self):
      print "\n[DISCONNECTION] %s disconnected" % self.id
      for _id, user in self.users.items():
        user.sendMessage("%s disconnected" % self.id)
        print "\n[FRAME] from %s to %s:\n%s disconnected" % (self.id, _id, self.id)

    def onMessage(self, msg):
      for _id, user in  self.users.items():
        user.sendMessage(msg)
        print "\n[FRAME] from %s to %s:\n%s" % (self.id, _id, msg)

  class WebSocketFactory(Factory):
    
    def __init__(self):
      self.users = {}
    
    def buildProtocol(self, addr):
      return WebSocketHandler(self.users)

  parser = argparse.ArgumentParser(
      description=__DESCRIPTION__,
      prog='python -m TwistedWebsocket.server'
    )
  parser.add_argument("-p","--port", help="Change listening port (default 9999).", type=int, default=9999)
  parser.add_argument("-ssl", help="Activate SSL.", action="store_true")
  parser.add_argument("-key", help="Path to your *.key file")
  parser.add_argument("-cert", help="Path to yout *.crt file")
  parser.add_argument("-v","--version", help="Show the package version and exit", action="store_true")
  options = parser.parse_args(sys.argv[1:]) 
  
  if options.version:
    print __VERSION__
    exit(0)

  if options.ssl == False:
    reactor.listenTCP(options.port, WebSocketFactory())
    print "TwistedWebsocket listening on port %s ..." % options.port
  else:
    if not options.key or not options.cert:
      parser.print_help()
      exit(-1) 
    with open(options.key) as keyFile:
      with open(options.cert) as certFile:
        cert = ssl.PrivateCertificate.loadPEM(keyFile.read() + certFile.read())
    reactor.listenSSL(options.port, WebSocketFactory(), cert.options())
    print "TwistedWebsocket listening on port %s with SSL ..." % options.port

  reactor.run()
