"""
"""
from multiprocessing import Process

class GenreIdentifier(Process):
    def __init__(self, gIdent):
        Process.__init__(self)
        #self.gIdent = gIdent
        #self.counter = 0
    def run(self):
        while True: #not self.counter:
            pass
            #res = self.gIdent.get()
            #if res:
            #    print(res)
            #    self.counter += 1
            
            
        