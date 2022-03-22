from scapy.utils import rdpcap
from reprint import output
from scapy.all import sendp, Ether
from time import sleep
import sys
from pathlib import Path

#if len(sys.argv)<2:
#    print('pass 1 argument: pcap file"')
#    exit(1)

#pcap_file = sys.argv[1]

# Path to the directory containing PCAP files
# This script will read all PCAP inside this directory
pcaps = Path("test-pcap-7th-rev")

counter = 1
class_counter = 0

with output(initial_len=2, interval=0) as output_lines:
    for pcap_file in sorted(pcaps.iterdir()):
        for packet in rdpcap(str(pcap_file)):
            if 'Ether' not in packet:
                packet = Ether()/packet
            if packet.haslayer('IP') == 1:
                packet['IP'].src = "10.0.1.1"
                packet['IP'].dst = "10.0.4.2"
                sendp(packet, iface="h1-eth0", verbose=False)
                output_lines[0] = "Replaying {}".format(pcap_file)
                output_lines[1] = "Number of sent packets: {}".format(counter)
                counter += 1
                #if class_counter < 3:
                sleep(1.4)
                #if counter > 32700:
                #    counter = 1
                #    break
        sleep(5)
