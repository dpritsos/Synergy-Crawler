
from multiprocessing import Pool

class test(Pool):
    def __init__(self):
        Pool.__init__(3)
        
    def feed(self):
        self.imap(self.count, [1,2,3], 3)
        
    def count(self, num):
        print num
            

c = test()

c.feed()        