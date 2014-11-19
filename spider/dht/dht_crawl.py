# -*- coding:utf-8 -*-

import socket
from hashlib import sha1
from random import randint
from bencode import bencode, bdecode
from socket import inet_ntoa
import struct

from threading import Timer, Thread

BOOTSTRAP_NODES = [
    ("router.bittorrent.com", 6881),
    ("dht.transmissionbt.com", 6881),
    ("router.utorrent.com", 6881)
]

class dht_node(object):
    def __init__(self, id, ip, port):
        self.id     = id
        self.ip     = ip
        self.port   = port

class node_bucket(object):
    def __init__(self):
        self.nodes = []

    def add(self, node):
        self.nodes.append(node)

    def remove(self, node):
        self.nodes.remove(node)

STRING_SPACE="abcdefghijklmnopqrstyvwxyz0123456789ABCDEFGHIJKLMNOPQRSTYVWXYZ"

class dht_krpc(object):
    def gen_random_str(self, length):
        return "".join( STRING_SPACE[randint(0,61)] for _ in xrange(length) )

    def gen_random_id(self, length=40):
         h = sha1()
         h.update( self.gen_random_str(length) )

         return h.digest()

    def query_head(self, method):
        return { "t":self.gen_random_str(2), "y":"q", "q":method }

    def ping(self, id):
        query      = self.query_head("ping")
        query["a"] = dict(id=id)

        return bencode(query)

    def find_peer(self, id, node):
        query      = self.query_head("find_node")
        query["a"] = dict(id=id, target=node)

        return bencode(query)

    def get_peers(self, id, torrent):
        query      = self.query_head("get_peers")
        query["a"] = dict(id=id, info_hash=torrent)

        return bencode(query)

    def announce_peer(self, id, torrent, port, token, implied_port=None):
        query       = self.query_head("announce_peer")
        query["a"] = {"id":("%s")%(id), "info_hash":torrent, "port":port, "token":token}

        if type(implied_port) is not None:
            query["a"]["implied_port"] = implied_port

        return bencode(query)

    def error_message(self, code, msg):
        resp = { "t":"aa", "y":"e", "e":[code, msg] }

        return bencode(resp)

    def decode_nodes(self, compact_nodes):
        nodes  = []
        length = len(compact_nodes)
        if length < 26:
            return nodes

        for i in range(0, length, 26):
            nid = compact_nodes[i:i+20]
            ip  = inet_ntoa(compact_nodes[i+20:i+24])
            port= struct.unpack("!H", nodes[i + 24:i + 26])[0]

            nodes.append( (nid, ip, port) )

class dht(object):
    def __init__(self, ip, port):
        self.ufd = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        self.ufd.bind( (ip, port) )

        self.krpc = dht_krpc()

        self.whoami = dht_node(self.krpc.gen_random_id(), ip, port)
        self.bucket = node_bucket()

    def send_krpc(self, msg, address):
        try:
            print(msg)
            self.ufd.sendto(msg, address)
        except Exception:
            pass

    def receive_krpc(self):
        try:
            (data, address) = self.ufd.recvfrom(65536)
            msg = bdecode( data )
            self.handle_message( msg, address )
        except Exception:
            pass

    def find_node(self, address):
        print(address)
        self.send_krpc( self.krpc.find_peer(self.whoami.id, self.krpc.gen_random_id()), address )

    def process_find_node_resp(self, msg, address):
        nodes = self.krpc.decode_nodes( msg["r"]["nodes"] )
        for node in nodes:
            print(node)
            self.bucket.add(node)

    def process_get_peers_req(self, msg, address):
        print( msg["a"]["info_hash"], address )
        self.send_krpc( self.krpc.error_message(202, "Server Error"), address )

    def join_dht(self):
        for address in BOOTSTRAP_NODES:
            self.find_node( address )

    def handle_message(self, msg, address):
        try:
            if msg["y"] == "r":
                if "nodes" in msg["r"]:
                    self.process_find_node_resp(msg, address)
            elif msg["y"] == "q":
                if msg["q"] == "get_peers":
                    self.process_get_peers_req(msg, address)
        except KeyError:
            pass

class dht_thread(Thread):
    def __init__(self, ip, port):
        Thread.__init__(self)

        self.dht = dht(ip, port)

    def run(self):
        self.dht.join_dht()

        while True:
            self.dht.receive_krpc()


if __name__ == "__main__":
    dht = dht_thread( "0.0.0.0", 6881 )
    dht.start()
    dht.join()
