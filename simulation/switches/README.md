# Switches

This folder contains all the stuff for simulating the network.


## switch_commands
This folder contains all the switch instructions. In normal condition, it usually consists of table entries for forwarding. However, in this thesis, it also contains instruction for writing NN weights to register. This weights are from the bnn-weights folder. Each switch may hold more than one NN layer. In this case, please be careful with the register index when converting the weights.

## nnsplit.p4
This is the main P4 code for the switches.

## p4app.json
This JSON file is the configuration file for the simulation. You can modify the simulation parameters in this file (like network topology, number of host, number of switches, etc.). P4Utils read this file to run simulation.


## **Running the experiment**
* Run `sudo p4run`. 
* After that, you may open switch 1, the sender and the receiver (eg. ` xterm s1 h1 h2`). You may need to set the max MTU with in all switches and in hosts to 65535 with `ifconfig <INTERFACE> mtu 65535`. Some packets are big and we need to allow that going through the network.
* Then, you may start the controller in the controller folder with `sudo python3 controller_nn.py <THRIFT-PORT>`. Thrift Port is the port of the egress switch. It is used to receive the activation from the switch. You can find the Thrift port of each switch in the log info when you run p4run.
* Finally, you can run the `receive_traffic.py` at the receiver and then `replay_pcap.py` at the sender.
* Observe the classification result in the controller.
