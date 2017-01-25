import time
import src

#step function template
# print "New Step~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
# for packet in network.packets.values():
#     if packet.timer > 0:
#         packet.decrement_timer()
#     elif packet.timer == 0:
#         packet.update_location()
#         if(packet.get_destination() == packet.current_node.node_id):
#             print packet.payload.ip_datagram.segment.message
#             del(network.packets[packet.packet_id])
#     else:
#         packet.update_location()
def test_step(network):
    """Step function for use in the simulation"""
    print "New Step~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    for packet in network.packets.values():
        print "packet #", packet.packet_id
        if packet.timer > 0:
            print "transmitting on connection", packet.connection.connection_id
            print "Time steps to completion: " + str(packet.timer)
            packet.decrement_timer()
        elif packet.timer == 0:
            packet.update_location()

            try:
                conn_id = packet.connection.connection_id
            except(AttributeError):
                conn_id = -1

            if conn_id == -1:
                print "packet", packet.packet_id, "has not been forwarded"
            else:
                print "packet", packet.packet_id, "has been forwarded onto connection", packet.connection.connection_id,\
                    "latency:", str(packet.connection.latency) + "."


            if(packet.get_destination() == packet.current_node.node_id):

                del(network.packets[packet.packet_id])
                print "packet", packet.packet_id, "has arrived at node", packet.current_node.node_id, "and been deleted."
                print "It was carrying the message:"
                print packet.payload.ip_datagram.segment.message
        else:
            print "packet", packet.packet_id, "has neg timer, so it's just starting."
            packet.update_location()

        print "packet is at node " + str(packet.current_node.node_id)



def table_step(network):
    print "New Step~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print get_packet_table()

    for packet in network.packets.values():
        if (packet.get_destination() == packet.current_node.node_id):
            print "Packet #" + str(packet.packet_id) + " delivered: " + packet.payload.ip_datagram.segment.message
        if packet.timer > 0:
            packet.decrement_timer()
        elif packet.timer == 0:
            packet.update_location()
        else:
            packet.update_location()

    time.sleep(1)

def get_packet_table():
    string = "Packet Table\n"

    for packet in src.Network.network.packets.values():
        conn_id = "NA"
        next = "NA"
        try:
            conn_id = packet.connection.connection_id
            next = packet.connection.other_node(packet.current_node).node_id
        except: pass
        finally:

            #The +1 takes into account the implicit one-step processing time for each packet on arrival
            ETA = packet.timer + 1
            if packet.timer == -1:
                ETA = "NA"

            string += "Pkt #" + str(packet.packet_id) + ":" + \
                " Loc " + str(packet.current_node.node_id) + \
                " Nxt " + str(next) +\
                " Src " + str(packet.get_source()) + \
                " Dst " + str(packet.get_destination()) + \
                " Conn " + str(conn_id) + \
                " ETA " + str(ETA)
            string += "\n"
    return string