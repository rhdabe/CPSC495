class Message:
    static_id = 0
    def __init__(self, msg):
        self.message = msg
        self.message_id = Message.static_id
        Message.static_id += 1

    def __str__(self):

        return 'MESSAGE:id%d message:%s' %(self.id, self.message)