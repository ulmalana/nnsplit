#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct

from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet, bind_layers, IPOption
from scapy.all import Ether, IP, UDP, TCP
from scapy.fields import *
from scapy.layers.inet import _IPOption_HDR

class BNNHeader(Packet):
    name = "BNN"
    fields_desc = [XByteField("type", 0),
                XByteField("bnn_result", 0)]

bind_layers(IP, BNNHeader)
bind_layers(BNNHeader, TCP)

class IPOption_BNN(IPOption):
    name = "BNN"
    #option = 31
    fields_desc = [ _IPOption_HDR,
                    #FieldLenField("length", None, fmt="B",  # Only option 0 and 1 have no length and value  # noqa: E501
                    #             length_of="bnn_result", adjust=lambda pkt, l:l),
                    #BitField("length", 0, 24),
                    BitField("bnn_input", 0, 56),
                    BitField("bnn_next_input", 0, 56),
                    BitField("output_result", 0, 4),
                    BitField("other", 0, 4)]

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

def main():

    if len(sys.argv)<3:
        print 'pass 2 arguments: <destination> "<tos>"'
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print "sending on interface %s to %s" % (iface, str(addr))
    pkt =  Ether(src=get_if_hwaddr(iface),dst = "00:00:00:00:01:12")
    #pkt = pkt /IP(dst=addr, tos=int(sys.argv[2]))
    pkt = pkt / IP(dst=addr) / TCP(dport=4070, sport=40594) / sys.argv[2] #/ BNNHeader(bnn_result=int())
    pkt.show()
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
