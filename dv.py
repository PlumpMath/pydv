from multiprocessing import Process, Queue
from server import start_agent_server
from job import JobEngine
from scheduler import Scheduler
from entity import entity, action, cmd
from visitor import visitor
from local import Local
from gcfengine import GCFEngine
from threading import Thread
import asyncio

@entity()
def foo3(self):
    @action(self)
    def build():
        print('foo3')
        yield from cmd("dir")

@entity()
def foo(self):
    self.need(foo3())
    @action(self)
    def build():
        print('foo')
        yield from cmd('dir')

@entity()
def foo2(self):
    @action(self)
    def build():
        print('foo2')

@entity()
def bar(self):
    self.need(foo())
    self.need(foo2())
    @action(self)
    def build():
        print('bar')

@visitor
def aa():
    yield from bar().build()
@visitor
def bb():
    yield from bar().build()

def main():

    in_q  = Queue()
    out_q = Queue()

    #loop = asyncio.get_event_loop()
    server_p = Process(target=start_agent_server, args=(in_q, out_q,))
    server_p.start()
    host, port = in_q.get()
    print("agent server start on {}:{}".format(host, port))
    
    GCFEngine.set_imp(Local(host, port))
    
    JobEngine.connect(in_q, out_q)

    while True:
        JobEngine.run()
        Scheduler.run()
        if len(JobEngine.running_cmds) > 0:
            m = in_q.get()
            in_q.put(m)
        else:
            break
        
    server_p.terminate()


if __name__ == '__main__':
    main()

