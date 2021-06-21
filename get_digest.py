import nnpy
import struct
import ipaddress
from p4utils.utils.topology import Topology
from p4utils.utils.sswitch_API import SimpleSwitchAPI
#from output_layer import predict_class
import socket

HOST = '127.0.0.1'
PORT = 65416


class DigestController():

    def __init__(self, sw_name):

        self.sw_name = sw_name
        self.topo = Topology(db="topology.db")
        self.sw_name = sw_name
        self.thrift_port = self.topo.get_thrift_port(sw_name)
        self.controller = SimpleSwitchAPI(self.thrift_port)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))

    def inttobit(n):
        return [1 if digit=='1' else -1 for digit in '{0:056b}'.format(n)]

    def predict_class(n):
        predictions = model.predict(np.array([inttobit(n)]))
        return np.argmax(predictions)



    def recv_msg_digest(self, msg):

        print(len(msg))
        topic, device_id, ctx_id, list_id, buffer_id, num = struct.unpack("<iQiiQi", msg[:32])

        msg = msg[32:]
        val = ""
        
        #7 bytes activation value
        print(struct.unpack(">BBBBBBB", msg[0:7]))
        for b in struct.unpack(">BBBBBBB", msg[0:7]):
            val = val+'{0:08b}'.format(b)

        self.s.sendall(val)
        print('val sent')

        self.controller.client.bm_learning_ack_buffer(ctx_id, list_id, buffer_id)

    def run_digest_loop(self):

        sub = nnpy.Socket(nnpy.AF_SP, nnpy.SUB)
        notifications_socket = self.controller.client.bm_mgmt_get_info().notifications_socket
        print("connecting to notification sub %s" % notifications_socket)
        sub.connect(notifications_socket)
        sub.setsockopt(nnpy.SUB, nnpy.SUB_SUBSCRIBE, '')

        while True:
            msg = sub.recv()
            self.recv_msg_digest(msg)


def main():
    DigestController("s5").run_digest_loop()

if __name__ == "__main__":
    main()
