
class Hardware(object):

    def __init__(self, id, type):
        self.id = id
        self.type = type

    def getValue(self):
        return 1
    
    def terminate(self):
        pass
        
    def __str__(self):
        return self.type+" #"+str(self.id)
        