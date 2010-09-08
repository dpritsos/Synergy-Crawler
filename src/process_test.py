
import multiprocessing

class test(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.count = 0
    def run(self):
        while True:
            self.count += 1
            print(self.count)
    def sofar(self):
        return self.count

if __name__ == "__main__":
    pt = test()
    pt.start()
    while True:
        print(pt.sofar(), pt.count) 