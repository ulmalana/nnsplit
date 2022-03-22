import nnpy, sys, os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import struct
import runtime_CLI
import sswitch_CLI
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from reprint import output
from datetime import datetime



class DigestController():

    def __init__(self, port):

        self.port = port
        pre_type = runtime_CLI.PreType.SimplePre

        services = runtime_CLI.RuntimeAPI.get_thrift_services(pre_type)
        services.extend(sswitch_CLI.SimpleSwitchAPI.get_thrift_services())

        standard_client, mc_client, sswitch_client = runtime_CLI.thrift_connect(
        'localhost', self.port, services)

        self.controller = sswitch_CLI.SimpleSwitchAPI(pre_type, standard_client, mc_client, sswitch_client)
        self.packet_counter = {0: 0, 1: 0, 2: 0, 3: 0}
        self.tr_class = 0

        self.inputs = keras.Input(shape=(56,), name="digits")
        self.outputs = layers.Dense(3, activation="softmax", name="predictions")(self.inputs)
        self.model = keras.Model(inputs=self.inputs, outputs=self.outputs)
        self.model.load_weights('bnn_56_traffic_weights-rev7.h5', by_name=True)

    def inttobit(self, n):
        #return [1 if digit=='1' else -1 for digit in '{0:056b}'.format(n.decode("utf-8"))]
        #self.data = n.decode("utf-8")
        return [1 if digit=='1' else -1 for digit in n]

    def predict_class(self, n):
        self.predictions = self.model.predict(np.array([self.inttobit(n)]))
        return np.argmax(self.predictions)

    def write_result(self, traf_class):
        time = datetime.now()
        result_file = open("results/result_"+str(traf_class)+"_"+str(time.strftime("%Y%m%d-%H:%M:%S"))+".txt", "w")
        result_file.write("############## Classification result. Class: "+str(traf_class)+" ##################\n\n")
        result_file.write("File Transfer: "+str(self.packet_counter[0])+" \n")
        result_file.write("Streaming: "+str(self.packet_counter[1])+" \n")
        result_file.write("Torrent: "+str(self.packet_counter[2])+" \n")
        result_file.write("Total Packets: "+str(self.packet_counter[3])+" \n")
        result_file.close()

    def class_counter(self, n):
        if n == 0:
            self.packet_counter[0] += 1
        elif n == 1:
            self.packet_counter[1] += 1
        elif n == 2:
            self.packet_counter[2] += 1
        #elif n == 3:
        #    self.packet_counter[3] += 1
        #elif n == 4:
        #    self.packet_counter[4] += 1
        #elif n == 5:
        #    self.packet_counter[5] += 1

        self.packet_counter[3] += 1
        if self.packet_counter[3] == 25000:
            self.write_result(self.tr_class)
            self.packet_counter[0] = 0
            self.packet_counter[1] = 0
            self.packet_counter[2] = 0
            self.packet_counter[3] = 0
            self.tr_class += 1


    def process_msg_digest(self, msg):

        #TODO : Create a handle for msg with length < 39 (usually 46, maybe contain 2 activation value [32:39] and [40:46])
        #print("got a digest. message length: "+str(len(msg)))
        topic, device_id, ctx_id, list_id, buffer_id, num = struct.unpack("<iQiiQi", msg[:32])
        self.controller.client.bm_learning_ack_buffer(ctx_id, list_id, buffer_id)

        msg = msg[32:]
        val = ""

        #print(struct.unpack(">BBBBBBB", msg[0:7]))
        for b in struct.unpack(">BBBBBBB", msg[0:7]):
            val = val+'{0:08b}'.format(b)

        return val


    def run_digest_loop(self):

        sub = nnpy.Socket(nnpy.AF_SP, nnpy.SUB)
        notifications_socket = self.controller.client.bm_mgmt_get_info().notifications_socket
        print("connecting to notification sub %s" % notifications_socket)
        sub.connect(notifications_socket)
        sub.setsockopt(nnpy.SUB, nnpy.SUB_SUBSCRIBE, '')
        print("connected. ready...")
        print("####### Classification Result ########")

        with output(initial_len=4, interval=0) as output_lines:
            while True:
                msg = sub.recv()
                digest_val = self.process_msg_digest(msg)

                prediction = self.model.predict(np.array([self.inttobit(digest_val)]))

                self.class_counter(int(np.argmax(prediction)))

                output_lines[0] = "File Transfer: {:d}".format(self.packet_counter[0])
                output_lines[1] = "Streaming: {:d}".format(self.packet_counter[1])
                output_lines[2] = "Torrent: {:d}".format(self.packet_counter[2])
                #output_lines[3] = "VPN File Transfer: {:d}".format(self.packet_counter[3])
                #output_lines[4] = "VPN Streaming: {:d}".format(self.packet_counter[4])
                #output_lines[5] = "VPN Torrent: {:d}".format(self.packet_counter[5])
                output_lines[3] = "Total packets: {:d}".format(self.packet_counter[3])


def main():
    if len(sys.argv)<2:
        print('pass 1 argument: port number"')
        exit(1)

    port = sys.argv[1]

    try:
        DigestController(port).run_digest_loop()

    except KeyboardInterrupt:
        print("closed...")
        exit(1)
    except:
        print("something's wrong...")
        exit(1)

if __name__ == "__main__":
    main()
