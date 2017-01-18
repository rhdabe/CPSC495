import test2
import src.Network

test2.init()
print test2.globvar
src.Network.network_init()
network = src.Network.network
if network != None: print "it worked"

list = [(0,1),(0,2)]
list2 = [(0,1),(0,2)]
print list2
for connection in list:
    list2.remove(connection)
    print list2