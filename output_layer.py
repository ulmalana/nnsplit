#!/usr/bin/env python3
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import socket
from reprint import output

inputs = keras.Input(shape=(56,), name="digits")
outputs = layers.Dense(6, activation="softmax", name="predictions")(inputs)
model = keras.Model(inputs=inputs, outputs=outputs)
model.load_weights('coba_bnn_56_traffic_weights.h5', by_name=True)

HOST='127.0.0.1'
PORT=65416

packet_counter = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5:0, 6: 0}

def inttobit(n):
    #return [1 if digit=='1' else -1 for digit in '{0:056b}'.format(n.decode("utf-8"))]
    data = n.decode("utf-8")
    return [1 if digit=='1' else -1 for digit in data]

def predict_class(n):
    predictions = model.predict(np.array([inttobit(n)]))
    return np.argmax(predictions)

def class_counter(n):
    if n == 0:
        packet_counter[0] += 1
    elif n == 1:
        packet_counter[1] += 1
    elif n == 2:
        packet_counter[2] += 1
    elif n == 3:
        packet_counter[3] += 1
    elif n == 4:
        packet_counter[4] += 1
    elif n == 5:
        packet_counter[5] += 1

    packet_counter[6] += 1

def print_percentage(pkt_counter):
    print("#######################################")
    print("File Transfer: {:.2f}".format(packet_counter[0]/packet_counter[6]))
    print("Streaming: {:.2f}".format(packet_counter[1]/packet_counter[6]))
    print("Torrent: {:.2f}".format(packet_counter[2]/packet_counter[6]))
    print("VPN File Transfer: {:.2f}".format(packet_counter[3]/packet_counter[6]))
    print("VPN Streaming: {:.2f}".format(packet_counter[4]/packet_counter[6]))
    print("VPN Torrent: {:.2f}".format(packet_counter[5]/packet_counter[6]))
    print("Total packets: {:d}".format(packet_counter[6]))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((HOST, PORT))
    s.listen()
    print("listening...")
    conn, addr = s.accept()
    with conn:
        print('connected by', addr)
        print("####### Classification Result ########")
        with output(initial_len=8, interval=0) as output_lines:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
        #print(type(data))
                class_counter(predict_class(data))
                #print_percentage(packet_counter)
                output_lines[0] = "File Transfer: {:.2f}".format(packet_counter[0]/packet_counter[6])
                output_lines[1] = "Streaming: {:.2f}".format(packet_counter[1]/packet_counter[6])
                output_lines[2] = "Torrent: {:.2f}".format(packet_counter[2]/packet_counter[6])
                output_lines[3] = "VPN File Transfer: {:.2f}".format(packet_counter[3]/packet_counter[6])
                output_lines[4] = "VPN Streaming: {:.2f}".format(packet_counter[4]/packet_counter[6])
                output_lines[5] = "VPN Torrent: {:.2f}".format(packet_counter[5]/packet_counter[6])
                output_lines[6] = "Total packets: {:d}".format(packet_counter[6])
except:
    s.close()
    print("Connection closed...")
