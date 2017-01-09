import test2
import src.Network

test2.init()
print test2.globvar
src.Network.network_init()
network = src.Network.network
if network != None: print "it worked"