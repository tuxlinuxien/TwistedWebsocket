# TwistedWebsocket

Websocket protocol implementation based on Twisted

/!\ Partial implementation of the [RFC 6455](https://www.rfc-editor.org/rfc/rfc6455.txt) /!\

## Requirements

  * Python 2.7+
  * [Twisted](https://twistedmatrix.com/trac/)

## Installation

  $ pip install TwistedWebsocket

## API
  - `TwistedWebsocket.Protocol.onConnect()`: Callback when the client is connected
  - `TwistedWebsocket.Protocol.onDisconnect()`: Callback when the client is disconnected
  - `TwistedWebsocket.Protocol.onMessage(msg)`: Callback when the client receive a message 
  - `TwistedWebsocket.Protocol.sendMessage(msg)`: Send a message to the client
  - `TwistedWebsocket.Protocol.users`: Dictionnary ( self == self.clients[self.id] ) off all the clients connected to the server
  - `TwistedWebsocket.Protocol.id`: Client UUID4 id

## Default Implementation

```python

  from twisted.internet.protocol import Factory
  from twisted.internet import reactor
  from TwistedWebsocket import TwistedWebsocket


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


```
