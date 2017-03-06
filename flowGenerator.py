import random
filename = "flow"

fh = open(filename, 'w')


randomlist = random.sample(range(16),16)

for i in range(16):
    client = (randomlist[i])
    server = (i)
    fh.write(str(client)+" "+str(server)+"\n")

'''
clientNum = 16
for _ in range(clientNum):
    client, server = random.sample(range(16),2)
    fh.write(str(client)+" "+str(server)+"\n")
'''

fh.close()
