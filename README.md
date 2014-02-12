TwistedWebsocket
================

Websocket server protocol implementation based on Twisted (Partial implementation of the RFC 6455)

Requirements
------------

-  Python 2.7+
-  Twisted

Installation
------------

::

  pip install TwistedWebsocket

API
---

-  ``TwistedWebsocket.server.Protocol.onConnect()``: Callback when the client is connected
-  ``TwistedWebsocket.server.Protocol.onDisconnect()``: Callback when the client is disconnected
-  ``TwistedWebsocket.server.Protocol.onMessage(msg)``: Callback when the client receive a message
-  ``TwistedWebsocket.server.Protocol.sendMessage(msg)``: Send a message to the client
-  ``TwistedWebsocket.server.Protocol.users``: Dictionnary ( self == self.clients[self.id] ) off all the clients connected to the server
-  ``TwistedWebsocket.server.Protocol.id``: Client UUID4 id

Default Implementation
----------------------

Broadcast server example:

::

  from twisted.internet.protocol import Factory
  from twisted.internet import reactor
  from TwistedWebsocket.server import Protocol


  class WebSocketHandler(Protocol):

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
     return WebSocketHandler(self.users)


  reactor.listenTCP(9999, WebSocketFactory())
  reactor.run()

TODO
----

-  Client protocol implementation
-  Improve frame building
