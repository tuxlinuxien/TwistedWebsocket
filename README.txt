TwistedWebsocket
================

Websocket server implementation based on Twisted with SSL support.

Requirements
------------

-  Python 2.7+
-  Twisted

Installation
------------

::
    
    pip install TwistedWebsocket

Testing
-------

::
    
    python setup.py test

    
Built-in broadcast server
-------------------------

A server is already integrated into TwistedWebsocket package.
::

    python -m TwistedWebsocket.server


Advanced options

::

    usage: python -m TwistedWebsocket.server [-h] [-p PORT] [-ssl] [-key KEY] [-cert CERT]

    Websocket server implementation based on Twisted with SSL support.

    optional arguments:
      -h, --help            show this help message and exit
      -p PORT, --port PORT  Change listening port (default 9999).
      -ssl                  Activate SSL.
      -key KEY              Path to your *.key file.
      -cert CERT            Path to yout *.crt file.



API
---

Frame manager

-  ``TwistedWebsocket.frame.Frame(buf)``: Create Frame instance
-  ``TwistedWebsocket.frame.Frame.message()``: Return decoded message from frame instance
-  ``TwistedWebsocket.frame.Frame.length()``: Return frame length from frame instance
-  ``TwistedWebsocket.frame.Frame.buildMessage(msg, mask=True)``: (@staticmethod) Create a websocket compatible frame. If mask == True, it will be a client->server frame.

Server Protocol

-  ``TwistedWebsocket.server.Protocol.onHandshake(header)``: Callback when HTTP-like client header is received
-  ``TwistedWebsocket.server.Protocol.onConnect()``: Callback when the client is connected
-  ``TwistedWebsocket.server.Protocol.onDisconnect()``: Callback when the client is disconnected
-  ``TwistedWebsocket.server.Protocol.onMessage(msg)``: Callback when the client receive a message
-  ``TwistedWebsocket.server.Protocol.sendMessage(msg)``: Send a message to the client
-  ``TwistedWebsocket.server.Protocol.users``: Dictionnary ( self == self.clients[self.id] ) off all the clients connected to the server
-  ``TwistedWebsocket.server.Protocol.id``: Client UUID4 id

Exceptions

-  ``TwistedWebsocket.exception.FrameError``
-  ``TwistedWebsocket.exception.ProtocolError``

Package information

-  ``TwistedWebsocket.server.__VERSION__``


Default Implementation
----------------------

Broadcast server example:

::

    from twisted.internet.protocol import Factory
    from twisted.internet import reactor
    from TwistedWebsocket.server import Protocol
    import re


    class WebSocketHandler(Protocol):

      def onHandshake(self, header):
        g = re.search('Origin\s*:\s*(\S+)', header)
        if not g: return
        print "\n[HANDSHAKE] %s origin : %s" % (self.id, g.group(1))

      def onConnect(self):
        print "\n[CONNEXION] %s connected" % self.id
        for _id, user in self.users.items():
          user.sendMessage("%s connected" % self.id)
          print "\n[FRAME] from %s to %s:\n%s connected" % (self.id, _id, self.id)

      def onDisconnect(self):
        print "\n[DISCONNEXION] %s disconnected" % self.id
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


    reactor.listenTCP(9999, WebSocketFactory())
    reactor.run()


WSS support
------------

::

    from twisted.internet.protocol import Factory
    from twisted.internet import reactor, ssl
    from TwistedWebsocket.server import Protocol
    import re

    class WebSocketHandler(Protocol):
      ...

    class WebSocketFactory(Factory):
      ...

    with open("./keys/ssl.localhost.key") as keyFile:
        with open("./keys/ssl.localhost.cert") as certFile:
          cert = ssl.PrivateCertificate.loadPEM(keyFile.read() + certFile.read())

    reactor.listenSSL(PORT, WebSocketFactory(), cert.options())
    reactor.run()


Generate self-signed SSL certificates:

::

    $> openssl genrsa -out ./keys/ssl.localhost.key 2048
    $> openssl req -new -x509 -key ./keys/ssl.localhost.key -out ./keys/ssl.localhost.cert -days 3650 -subj /CN=ssl.localhost

TODO
----

-  Improve frame building
-  Add WSS example with self-signed certificates
