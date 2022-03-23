# NNSPlit

This repository contains NNSplit codes for my thesis  ["On Supporting Large Neural Networks Model Implementation in Programmable Data Plane"](https://hdl.handle.net/11296/b9spqb) which was published in 2021.

In short, NNSplit is a technique for splitting neural networks layers and distributing the computational burden across data planes.


## Abstract
Neural networks algorithms are known for their high accuracy and are heavily used to solve many problems in various fields. With its proven capability in various tasks, embedding neural networks algorithms in the data plane is an appealing and promising option. This is possible with the emergence of P4 language to control the data plane. However, current data plane technology still has many constraints to implement complex functions. Most data planes have limited memory size and a limited set of operations. In addition, it is also widely known that neural networks are computationally expensive. Generally, a complex neural networks architecture is required for achieving high accuracy. Yet, with a complex architecture, it will affect the data plane’s forwarding capability as the main function. Therefore, minimizing the performance cost caused by implementing neural networks algorithms in the data plane is critical.

This thesis proposes a technique called NNSplit for solving the performance issue by splitting neural networks layers into several data planes. By splitting the layers, NNSplit distributes the computational burden from implementing neural networks across data planes. For supporting layer splitting, a new protocol called SØREN is also proposed. SØREN protocol header carries the activation value and bridges neural network layers in all switches. In our implementation, we consider a use case of multi-class traffic classification. 

The result from experiments using Mininet and BMv2 show that NNSplit can reduce memory usage by almost 50% and increase the throughput compared to non-splitiing scenario, with a cost of small additional delay of 14%. In addition, adding SØREN protocol in the packet brings only a small impact of 213 µs in terms of processing time. The results suggest that our method can support a large neural networks model in the data plane with a small performance cost.

## Got Questions?
You may reach me at muhamaul@gmail.com
