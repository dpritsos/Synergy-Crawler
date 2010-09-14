

from multiprocessing import Process
import time

ps = list()

def printme():
    for i in xrange(1000):
        print("PRINT %s\n" % i)

while True:    
    for i in xrange(10000):
        ps.append( Process(target=printme) )
        ps[(len(ps) - 1)].start()
        print(len(ps))
    time.sleep(5)
    count = 0
    for p in ps:
        count += 1
        if not p.is_alive():
            print("Remove PROCESS %s" % count)
            p.join()
            ps.remove(p)
    

