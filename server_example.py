from twisted.internet.protocol import Factory
from twisted.internet import reactor
from TwistedWebsocket.server import Protocol


class WebSocketHandler(Protocol):

  def onConnect(self):
    for _id, user in self.users.items():
      user.sendMessage("%s connected" % self.id)

  def onDisconnect(self):
    for _id, user in self.users.items():
      user.sendMessage("%s disconnected" % self.id)

  def onMessage(self, msg):
    for _id, user in  self.users.items():
      user.sendMessage(msg)


class WebSocketFactory(Factory):
  
  def __init__(self):
    self.users = {}
  
  def buildProtocol(self, addr):
    return WebSocketHandler(self.users)


reactor.listenTCP(9999, WebSocketFactory())
reactor.run()
