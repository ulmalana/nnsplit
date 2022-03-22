# Simulation Scripts for 4 Layers BNN

This folder contains the necessary stuff to run NNSplit in 4 Layers BNN. Inside this folder, there are several subfolder as follows:

## bnn-weights
This folder contains the weights from the trained model (from the Jupyter Notebook) and ``weight_to_command.py`` script to convert the weight of a NN layer to readily-used P4Runtime command. Copy all the instructions (starting with ``register_write``) to the **switch_command** folder. **Please be careful with the register index when converting the weights. You may need to modify the index number in ``weight_to_command.py``.**

## controller
This folder contains ``controller_nn.py`` as the controller. This script reads the NN weights from the H5 file. The H5 file is produced from the trained model (Jupyter Notebooks, together with the weights from the bnn_weights folder). The results subfolder is used to contain the classification results.

## switch_commands
This folder contains all the switch instructions. In normal condition, it usually consists of table entries for forwarding. However, in this thesis, it also contains instruction for writing NN weights to register. This weights are from the bnn-weights folder. Each switch may hold more than one NN layer. In this case, please be careful with the register index when converting the weights.

## nnsplit.p4
This is the main P4 code for the switches.

## p4app.json
This JSON file is the configuration file for the simulation. You can modify the simulation parameters in this file (like network topology, number of host, number of switches, etc.). P4Utils read this file to run simulation.

## receive_traffic.py
This Python script is used to display the received traffic from a host. It is helpful to check whether the number of received packets in the host is the same as the received packets in the switch (it may be different, see the explanation below in ``set_mtu.sh``.)

## replay_pcap.py 
This Python script is used to replay PCAP files. It reads every packet in the PCAP file then send the packet to the destination. You can create a folder with PCAP files inside and this script will simulate the traffic based on them.

## set_mtu.sh
This script is used to set MTU of all the switch to maximum (65535). This will help to simulate all the packet because some of the packets are large and it may not be sent without changing the maximum MTU with this script.

## **Running the experiment**
* Run ``sudo p4run ``. 
* After that, you may open switch 1, the sender and the receiver (eg. `` xterm s1 h1 h2``). In S1, you may set the max MTU with ``set_mtu.sh`` and in hosts you may use ``ifconfig <INTERFACE> mtu 65535``. 
* Then, you may start the controller in the controller folder with ``sudo python3 controller_nn.py <THRIFT-PORT>``. Thrift Port is the port of the egress switch. It is used to receive the activation from the switch. You can find the Thrift port of each switch in the log info when you run p4run.
* Finally, you can run the ``receive_traffic.py`` at the receiver and then ``replay_pcap.py`` at the sender.
* Observe the classification result in the controller.
