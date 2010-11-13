
class Account(object):
    num_accounts = 0
    
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        Account.num_accounts += 1
        
    def __del__(self):
        Account.num_accounts -= 1
        
    def deposit(self, amt):
        self.balance = self.balance + amt
        
    def withdraw(self, amt):
        self.balance = self.balance - amt
        
    def inquiry(self):
        return self.balance
    
    
Account.num_accounts
Account.deposit
Account.inquiry

class Foo(object):
    def bar(self):
        print ("bar!")
        
    def spam(self):
        bar(self)       #Incorrect! 'bar' generates a NameError
        self.bar()      #This works
        Foo.bar(self)   #This also works
        
#Decriptors example
class TypeProperty(object):
    def __init__(self, name, type, default=None):
        self.name = "_" + name
        self.type = type
        self.default = default if default else type()
        
    def __get__(self, instance, cls):
        return getattr(instance, self.name, self.default)
    
    def __set__(self, instace, value):
        if not isinstance(value, self.type):
            raise TypeError("Must be a %s" % self.type)
        setattr(instace, self.name, value)
        
    def __delete__(self, instace):
        raise AttributeError("Can't delete attribute")
    
class Foo(object):
    name = TypeProperty("name", str)
    num = TypeProperty("num", int, 42)


f = Foo()
a = f.name       #Implicitly calls Foo.name.__get__(f, Foo)
f.name = "Guido" #Calls Foo.name.__set__(f, "Guido")
del f.name       #Calls Foo.name.__delete__(f)   
    
    