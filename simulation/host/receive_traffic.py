#!/usr/bin/env python

# NOTE: THIS SCRIPT IS STILL IN PYTHON 2

import sys
import struct
import os

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr, bind_layers
from scapy.all import Packet, IPOption, Ether
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, UDP, Raw
from scapy.layers.inet import _IPOption_HDR
from scapy.fields import *
#from collections import Counter

#packet_counts = Counter()
count = 0


def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

def handle_pkt(pkt):
    global count
    if 'IP' in pkt:
        if pkt['IP'].src == "10.0.1.1":
            count += 1
            return ("#{} {} ==> {}: ".format(count, pkt['IP'].src, pkt['IP'].dst))

    sys.stdout.flush()

def main():
    ifaces = filter(lambda i: 'eth' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "sniffing on %s" % iface
    sys.stdout.flush()
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
