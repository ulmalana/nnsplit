# Host

This folder contains the necessary scripts for simulating the traffic.

## receive_traffic.py
This Python script is used to display the received traffic from a host. It is helpful to check whether the number of received packets in the host is the same as the received packets in the switch (it may be different, see the explanation below in ``set_mtu.sh``.)

## replay_pcap.py 
This Python script is used to replay PCAP files. It reads every packet in the PCAP file then send the packet to the destination. You can create a folder with PCAP files inside and this script will simulate the traffic based on them.
