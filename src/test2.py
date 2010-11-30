
from multiprocessing import Pool
import copy_reg
import types


def _pickle_method(method):
    func_name = method.im_func.__name__
    print func_name
    #obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, cls)

def _unpickle_method(func_name, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(cls)


copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)


class test(object):
    def __init__(self):
        self.p = Pool(3)
        
    def feed(self):
        self.p.imap(self.test, [1,2,3], 3)
        
    #def __getstate__(self):
    #    return self.__dict__['__count1']
    
    #def __setstate__(self, _method):
    #    self.__dict__ ['__count1']= _method
    
    def test(self, num):
        print num
            
    def pclose(self):
        self.p.close()
        self.p.join()

c = test()

c.feed()  
c.pclose()