class InvalidTransportProtocol(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class InvalidApplicationProtocol(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)