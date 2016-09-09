from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

import json
import random


class KommandozentraleClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        self.sendMessage(b'{"id":1, "method":"subscribe", "params":{"key":"test"}}')
        self.sendMessage(b'{"id":2, "method":"subscribe", "params":{"key":"test"}}')
        self.sendMessage(b'{"id":3, "method":"subscribe", "params":{"key":"test"}}')
        self.sendMessage(b'{"id":4, "method":"unsubscribe", "params":{"key":"test"}}')
        self.sendMessage(b'{"id":5, "method":"unsubscribe", "params":{"key":"test"}}')
        self.sendMessage(b'{"id":6, "method":"unsubscribe", "params":{"key":"test"}}')
        self.sendMessage(b'{"id":7, "method":"rpc", "params":{"module_id":"test_lampe","method":"getConfig"}}')
        self.sendMessage(b'{"id":8, "method":"rpc", "params":{"module_id":"test_lampe","method":"on"}}')
        self.sendMessage(b'{"id":9, "method":"sdflkjh"}')
        #self.sendClose()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            res = json.loads(payload.decode('utf8'))
            print(res)
            if not "error" in res["result"]:
                if res["result"] == "state":
                    print("State of {switch}: {state}".format(**res))
                elif res["result"] == "config":
                    print(res)
                    self.sendClose()
                else:
                    print(res)
            else:
                print("An error occured: {0}".format(res["result"]["error"]))

    def onClose(self, wasClean, code, reason):
        loop.stop()


if __name__ == '__main__':

    import asyncio

    factory = WebSocketClientFactory(u"ws://localhost:9000")
    factory.protocol = KommandozentraleClientProtocol

    loop = asyncio.get_event_loop()
    connection = loop.create_connection(factory, 'localhost', 9000)
    loop.run_until_complete(connection)
    loop.run_forever()
    loop.close()