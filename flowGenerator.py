import random
filename = "flow"

fh = open(filename, 'w')

clientNum = 16

for _ in range(clientNum):
    client, server = random.sample(range(16),2)
    fh.write(str(client)+" "+str(server)+"\n")

fh.close()
