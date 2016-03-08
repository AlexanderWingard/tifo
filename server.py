import sys
import json
import numpy as np
import cv2

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File
from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredQueue
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from autobahn.twisted.resource import WebSocketResource

clients = []
queue = DeferredQueue()
cap = cv2.VideoCapture(0)

def capture(num):
    lower = np.array([0, 0,200], dtype = "uint8")
    upper = np.array([180, 180, 255], dtype = "uint8")
    ret, im = cap.read()

    thresh = cv2.inRange(im, lower, upper)
    contours, h = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea,reverse=True)[:1]

    if len(contours) > 0:
        rect = cv2.minAreaRect(contours[0])
        box = cv2.cv.BoxPoints(rect)
        return {'msg': 'rect', 'rect': box, 'shape': im.shape}
    else:
        return {'msg': 'fail'}

@inlineCallbacks
def master(queue):
    while True:
        client = yield queue.get()
        client.sendMessage(json.dumps({'msg' : 'bg', 'color' : 'red'}))
        res = yield capture(len(clients))
        client.sendMessage(json.dumps({'msg' : 'bg', 'color' : 'white'}))
        client.sendMessage(json.dumps(res))

class WSProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        pass

    def onOpen(self):
        clients.append(self)
        queue.put(self)

    def onMessage(self, payload, isBinary):
        pass

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        clients.remove(self)


if __name__ == '__main__':
    master(queue)
    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:8080")
    factory.protocol = WSProtocol

    resource = WebSocketResource(factory)

    root = File("./static")
    root.putChild(u"ws", resource)

    site = Site(root)
    reactor.listenTCP(8080, site)

    reactor.run()
