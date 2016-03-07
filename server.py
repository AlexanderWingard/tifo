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

def capture(num):
    lower = np.array([0, 0,200], dtype = "uint8")
    upper = np.array([180, 180, 255], dtype = "uint8")
    #cap = cv2.VideoCapture(0)
    #while(True):
    #ret, im = cap.read()
    #cap.release()
    im = cv2.imread('static/test{}.jpg'.format(max(min(2, (num % 3)), 1)))
    thresh = cv2.inRange(im, lower, upper)
    contours, h = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea,reverse=True)[:1]

    # for cnt in contours:
    #     rect = cv2.minAreaRect(cnt)
    #     box = cv2.cv.BoxPoints(rect)
    #     box = np.int0(box)
    #     cv2.drawContours(im,[box],0,(0,255,0),2)

    if len(contours) > 0:
        rect = cv2.minAreaRect(contours[0])
        box = cv2.cv.BoxPoints(rect)
        return {'msg': 'rect', 'rect': box, 'shape': im.shape}
    else:
        return {'msg': 'fail'}

    #im = cv2.resize(im, (640, 480))
    # cv2.imwrite('static/test.png', im)
    #cnt = cv2.imencode('.jpg',im)[1]
    #b64 = base64.encodestring(cnt)
    # cv2.imshow('image',im)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     pass

    # cv2.destroyAllWindows()

    #return b64

@inlineCallbacks
def master(queue):
    while True:
        client = yield queue.get()
        client.sendMessage(json.dumps({'msg' : 'bg', 'color' : 'red'}))
        yield sleep(2)
        res = yield capture(len(clients))
        client.sendMessage(json.dumps({'msg' : 'bg', 'color' : 'white'}))
        for c in clients:
            c.sendMessage(json.dumps(res))

class WSProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        clients.append(self)
        print("WebSocket connection request: {}".format(request))

    def onOpen(self):
        queue.put(self)
        # res = yield capture()
        # self.sendMessage(res.encode("UTF-8"), False)

    def onMessage(self, payload, isBinary):
        for c in clients:
            c.sendMessage(payload, isBinary)

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
