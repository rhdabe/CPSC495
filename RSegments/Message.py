class Message:

    # TODO add application layer protocol field
    # TODO add transport layer protocol field
    static_id = 0
    def __init__(self, msg, s_IP, d_IP,a_p = "Default", t_p = "UDP"):
        self.message = msg
        self.message_id = Message.static_id
        self.src_IP = s_IP
        self.dest_IP = d_IP
        self.application_protocol = a_p
        self.transport_protocol = t_p
        Message.static_id += 1

    def __str__(self):
        return 'MESSAGE:id:%d ap:%s tp:%s message:%s' %(self.message_id, self.application_protocol,
                                                        self.transport_protocol, self.message)