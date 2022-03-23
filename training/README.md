# Notes about this directory
I built my neural networks models with the Jupyterbook file in this directory. You may find all the neccessary library inside Jupyterbook file. I used [ISCXVPN2016](https://www.unb.ca/cic/datasets/vpn.html) dataset for building the model.

The expected results from the training phase are:
* **Binarized weights from each neuron** (`w-l*.txt` files in `bnn_weights` directory). 
These weights will be written into the switch/data plane register. You can use `weight_to_command.py` script to generate the commands for inserting the weights. `s*.txt` files are the example of the generated commands. 
*  **NN weights of the last layer (not binarized)** 
This real-valued weights will be used in the controller for inference. Using binarized weights in the controller doesn't lead to good inference results. You may find later or have seen the H5 file containing the real-valued weights in the simulation directory.
