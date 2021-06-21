#create switch commands to insert bnn weights

import sys

if len(sys.argv)<3:
        print('pass 2 arguments: <weights file> "<switch commands file>"')
        exit(1)

data = [line.strip() for line in open(str(sys.argv[1]), "r")]

command = open(str(sys.argv[2]), "w")
#command.write("coba baris 1\ncoba baris 2\n")
for i, element in enumerate(data):
	command.write("register_write MyIngress.weights_bnn "+str(i)+" "+str(element)+" \n")

command.close()
