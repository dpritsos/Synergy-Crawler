"""
SynCIOScheduler is a asynchronous I/O micro-scheduler for improving the performance of the SynCrawler. In particular is using a Event-Driven
model and more specifically the trampoline model, implemented with Python Coroutines and microThreading (or greenThreading) concept.

This micro-Scheduler handles custom made Events for asynchronous I/O handling, which they will function like "System Calls". The micro-Scheduler
is invoked only when an I/O handing is required. The handing of the I/O Events is transparent to the rest of the code flow so it can easily
integrated to an MultiThreading or MultiProcessing code flow or an other Event-Driven (ie Coroutine/Generator based) code flow

The main consept of the code is ispired from David M. Beazleys book "Python Essential Reference"      
 
Author:Dimitrios Pritsos
Last Update: 8 Jul 2010

"""
import collections
import select
import types

class SynCIOScheduler(object):
    
    def __init__(self):
        self.TaskQ = collections.deque()
        self.ReadWaiting = {}
        self.WriteWaiting = {}
        self.numTasks = 0
        
    def run(self, count=-1, timeout=None):
        while self.numTasks:
            #Check for I/O events to handle
            if self.ReadWaiting or self.WriteWaiting:
                wait = 0 if self.TaskQ else timeout
                r, w, e = select.select(self.ReadWaiting, self.WriteWaiting, [], wait)
                for fileno in r:
                    self.schedule(self.ReadWaiting.pop(fileno))
                for fileno in w:
                    self.schedule(self.WriteWaiting.pop(fileno))
            #Run all the SystemCalls on the Que that are ready to run
            while self.TaskQ:
                    task = self.TaskQ.popleft()
                    try:
                        result = task.run()
                        if isinstance(result, SystemCall):
                            result.handle(self, task)
                        else:
                            self.schedule(task)
                    except StopIteration:
                        self.numTasks -= 1
            else:
                #If no task can run, we decide if we wait or return
                if count > 0:
                    count -= 1
                if count == 0:
                    return
                
    def new(self, Task):
        """Create a new task out of a coroutine"""
        newTask = TaskWrapper(Task)
        self.schedule(newTask)
        self.numTasks += 1
        
    def schedule(self, Task):
        """Put a task on the taskQueue"""
        self.TaskQ.append(Task)
        
    def readwait(self, Task, fd):
        """Have a task wait for data on file descriptor"""
        self.ReadWaiting[fd] = Task
        
    def writewait(self, Task, fd):
        """Have a task wait for writing on a file descriptor"""
        self.WriteWaiting[fd] = Task
    
    
class TaskWrapper(object):
    """This a Lightweight task wrapper which actually helps the scheduler to handle the a Coroutine/Generator as a Task"""
    
    def __init__(self, CoroutineOrGenerator):
        #Stores a Coroutine that works as System Call
        self.task = CoroutineOrGenerator
        #Value to send when resuming
        self.sendval = None
        #Call Stack
        self.stack = []
        
    def run(self):
        try:
            result = self.task.send(self.sendval)
            if isinstance(result, SystemCall):
                return result
            if isinstance(result, types.GeneratorType):
                self.stack.append(self.task)
                self.sendval = None
                self.task = result
            else:
                if not self.stack:
                    return
                self.sendval = result
                self.target = self.stack.pop()
        except StopIteration:
            if not self.stack:
                raise
            self.sendval = None
            self.target = self.stack.pop()
        
        
class SystemCall(object):
    """It represents as System Call"""
    def handle(self, sched, task):
        pass

#Implementation of different system calls
class ReadWait(SystemCall):
    
    def __init__(self, f):
        self.f = f
        
    def handle(self, sched, task):
        fileno = self.f.fileno()
        sched.readwait(task, fileno)


class WriteWait(SystemCall):
    
    def __init__(self, f):
        self.f = f
        
    def handle(self, sched, task):
        fileno = self.f.fileno()
        sched.writewait(task, fileno)


#I THINK I DONT REALY NEED THIS
class NewTask(SystemCall):
    
    def __init__(self, Task):
        self.newtask = Task
        
    def handle(self, sched, task):
        sched.new(self.newtask)
        sched.schedule(task)    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
     