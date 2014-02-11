from twisted.internet.protocol import Factory
from twisted.internet import reactor
import TwistedWebsocket


class ClientWebSocket(TwistedWebsocket.Protocol):

  def onConnect(self):
    for k, c in self.users.items():
      c.sendMessage("%s connected" % self.id)

  def onDisconnect(self):
    for k, c in self.users.items():
      c.sendMessage("%s disconnected" % self.id)

  def onMessage(self, msg):
    for _id, user in  self.users.items():
      user.sendMessage(msg)


class WebSocketFactory(Factory):
  
  def __init__(self):
    self.users = {}
  
  def buildProtocol(self, addr):
    return ClientWebSocket(self.users)


reactor.listenTCP(9999, WebSocketFactory())
reactor.run()