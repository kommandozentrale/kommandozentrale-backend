import yaml
import os
import asyncio
import json
import importlib
import copy
import re
import logging

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory


class KommandozentraleServerFactory(WebSocketServerFactory):
    clients = []

    modules = {}
    groups = {}
    def __init__(self, config, *args, **kwargs):
        WebSocketServerFactory.__init__(self, *args, **kwargs)
        for module_name, module_data in config["modules"].items():
            module_import_name = re.sub('(?!^)([A-Z]+)', r'_\1', module_data["type"]).lower()
            self.modules[module_name] = module_data

            module_module = importlib.import_module("modules."+module_import_name)
            module_object = getattr(module_module, module_data["type"])
            self.modules[module_name]["module_object"] = module_object(**module_data)

    def register(self, client):
        client_objects = [item for item in self.clients if item["client_object"] == client]
        if len(client_objects) == 0:
            self.clients.append({"client_object":client, "sub":[]})

    def unregister(self, client):
        client_objects = [item for item in self.clients if item["client_object"] == client]
        if len(client_objects) == 1:
            self.clients.remove(client_objects[0])

    def broadcast(self, key, msg):
        if not isinstance(msg, str):
            msg = json.dumps(msg)
        msg = msg.encode("utf8")
        for c in self.clients:
            if key in c["sub"]:
                client = c["client_object"]
                client.sendMessage(msg)

    def subscribe(self, client, key):
        client_objects = [item for item in self.clients if item["client_object"] == client]
        if key not in client_objects[0]["sub"]:
            client_objects[0]["sub"].append(key)

        logging.debug("Clients: {}".format(self.clients))

        return client_objects[0]["sub"]

    def unsubscribe(self, client, key):
        client_objects = [item for item in self.clients if item["client_object"] == client]
        if key in client_objects[0]["sub"]:
            client_objects[0]["sub"].remove(key)
        return client_objects[0]["sub"]


class KommandozentraleServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)
        self.factory.broadcast("key", "msg")

    def onClose(self, *args, **kwargs):
        WebSocketServerProtocol.onClose(self, *args, **kwargs)
        self.factory.unregister(self)

    def sendJsonMessage(self, message):
        message_str = json.dumps(message)
        message_bytes = message_str.encode()
        self.sendMessage(message_bytes)

    def getConfig(self, module):
        config_fields = ["name","public_methods"]
        config = {}
        for field in config_fields:
            config[field] = getattr(module, field)
        return config

    @asyncio.coroutine
    def onMessage(self, payload, isBinary):
        """ Handle messages """
        if not isBinary:
            req = json.loads(payload.decode('utf8'))

            req_id = req["id"] if "id" in req else None
            if "id" in req: del req["id"]

            result = None

            if req["method"] == "subscribe":
                result = self.factory.subscribe(self, req["params"]["key"])

            elif req["method"] == "unsubscribe":
                result = self.factory.unsubscribe(self, req["params"]["key"])

            elif req["method"] == "rpc" and isinstance(req["params"], dict) \
                and "module_id" in req["params"] and "method" in req["params"]:
                logging.debug(req)
                module = self.factory.modules[req["params"]["module_id"]]["module_object"]
                method = req["params"]["method"]
                
                del req["params"]["module_id"]
                del req["params"]["method"]

                if method in module.public_methods:
                    result = getattr(module, method)(**req["params"])

                elif method == "getConfig":
                    result = self.getConfig(module)

                

            else:
                result = {"error":"invalid request"}

            if req_id != None and result != None:
                self.sendJsonMessage({"result":result, "id":req_id})


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    assert os.path.isfile("config.yml"), "You need to create a \"config.yml\""
    with open("config.yml") as configfile:
        config = yaml.load(configfile)
        logging.debug(config)
    
    factory = KommandozentraleServerFactory(config)
    factory.protocol = KommandozentraleServerProtocol

    loop = asyncio.get_event_loop()
    server = loop.create_server(factory, 'localhost', 9000)
    ruc = loop.run_until_complete(server)
    logging.info("Started, listening on port 9000")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        ruc.close()
        loop.close()