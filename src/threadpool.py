
""" Thread Pool: Implemented as part of the Synergy-Crawler
    Author: Dimitrios Pritsos
    Last update: 12 / Nov / 2010"""

from threading import Condition, Thread, Event 
import Queue
import time

class WorkerThread(Thread):
    """Worker Thread class"""
       
    def __init__(self, tasks_queue, joinall):
        Thread.__init__(self)
        self.__tasks_queue = tasks_queue
        self.__joinall = joinall
        
    def run(self): 
        #Run while no Join-all signal has sent
        while not self.__joinall.is_set():
            #Suspend until a new task pending to be execute
            func, args, callback = (None, None, None)
            try: 
                func, args, callback = self.__tasks_queue.get(timeout=10)
                assert func, "ThreadPool Error: <None> function was given for execution"
            except Queue.Empty:
                if self.__joinall.is_set():
                    return
            #If func is a proper callable (i.e. No Queue.Empty exception has raised) 
            if callable(func):
                if callback:
                    callback( func( args ) )
                    self.__tasks_queue.task_done()
                else:
                    func( args )
                    self.__tasks_queue.task_done()

class ThreadPool(object):
    """Thread pool class: Creates a pool of threads and dispatches 
    tasks to the available threads."""
    
    def __init__(self, threads_num):
        self.__threads_l = list()
        self.__tasks_q = Queue.Queue() #Maybe this should be limited
        self.__joinall = Event()     
        self.__start_pool(threads_num)

    def __start_pool(self, threads_num):
        """Set the pool size and start all threads"""
        #Initialise the Threads
        for i in range(threads_num):
            self.__threads_l.append( WorkerThread(self.__tasks_q, self.__joinall) )
        #Start the threads
        for t in self.__threads_l:
            t.start()

    def dispatch(self, *args):
        #This IF statement is only for self.map() function  
        if isinstance(args[0], tuple):
            args = args[0]
        #Check for proper number of arguments and fill the missing arguments 
        if len(args) == 3:
            self.__tasks_q.put( args )
        elif len(args) == 2:
            #If no callback-function is given return the result of the dispatched function to the dispatch caller
            #in that case this function waits until the results are available
            return_l = list()
            self.__tasks_q.put( (args[0], args[1], return_l.append) )
            while not return_l: #Maybe this should be become NON-BLOCKING
                pass
            return return_l[0]
        elif len(args) == 1:
            self.__tasks_q.put( (args[0], None, None) )
        else:
            raise Exception("ThreadPool spawn() Error: Bad number of argument has given")
    
    def map(self, func, callback=None, iterable=None):
        #Maps the self.dispatched function to all the date in a multi-threading manner 
        if callback:
            args_l = map( lambda i:(func, iterable[i], callback), range(len(iterable)) ) 
            for args in args_l:
                self.dispatch(args)
        else:
            args = map( lambda i:(func, iterable[i]), range(len(iterable)) ) 
            return map( lambda i: self.dispatch( args[i] ), range(len(args)) )
        #MAYBE an imap() (i.e. iterable object) function should be implemented too
    
    def join_all(self, timeout=None):
        """Clear the task queue and terminate all threads in Pool"""
        if timeout:
            self.__joinall.set()
            time_slice = float(timeout) / float( len(self.__threads_l) )
            for t in self.__threads_l:
                t.join(time_slice)
                del t
        else: 
            self.__tasks_q.join()
            self.__joinall.set() 
            for t in self.__threads_l:
                t.join()
                del t
    
    def count_threads(self):
        return len(self.__threads_l)


#Unit Test
if __name__ == "__main__":
    
    print "Unit test is running\n"
    
    # Simple task for testing
    def sorting(data):
        print("SortTask starting for: %s" % data)
        data.sort()
        print("SortTask done for: %s" % data)
        return "Data Sorted: ", data

    #Simple Callback_func for testing
    def callback_func(data):
        print("Callback Function => sorting() returned: %s \n" % str( data ) )

    #A pool or some worker threads 
    pool = ThreadPool(10)

    #Dispatch some tasks to the Thread Pool (i.e. put some entries at the task Queue of the ThreadPool instance)
    pool.dispatch(sorting, [5, 6, 7, 1, 3, 0, 1, 1, 10], callback_func)
    pool.dispatch(sorting, [5], callback_func)
    pool.dispatch(sorting, [0, 0, 1, 10], callback_func)
    print("\npool.dispatch( sorting(), [ list ] ) returns: %s %s\n" % pool.dispatch(sorting, [5, 6, 7, 1, 3]) )   
    print("pool.map() returns: %s \n\n" %  pool.map( sorting, iterable=([12, 1], [11, 1], [10, 1], [9, 1], [8, 1], [7, 1], [6, 1], [5, 1], [4, 1], [3, 1], [2, 1], [1, 1], [0, 1]) ) )
    pool.map( sorting, callback=callback_func, iterable=([12, 1], [11, 1], [10, 1], [9, 1], [8, 1], [7, 1], [6, 1], [5, 1], [4, 1], [3, 1], [2, 1], [1, 1], [0, 1]) ) 
       
    #Terminate all threads when there are no other task for execution 
    pool.join_all()
    
    print("Thank you and Goodbye!")