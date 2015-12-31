#!/usr/bin/env python3.4

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
import signal
from utils import require

server_p = None

def cleanup():
    if server_p:
        server_p.terminate()
    JobEngine.cleanup()

def handler(signum, frame):
    cleanup() 
    exit(-1) 

#signal.signal(signal.SIGINT, handler)
#signal.signal(signal.SIGTERM, handler)

def main():

    global server_p

    in_q  = Queue()
    out_q = Queue()

    #loop = asyncio.get_event_loop()
    server_p = Process(target=start_agent_server, args=(in_q, out_q,))
    #server_p = Thread(target=start_agent_server, args=(loop, in_q, out_q,))
    server_p.start()

    try:
        host, port = in_q.get()

        print("agent server start on {}:{}".format(host, port))
    
        GCFEngine.set_imp(Local(host, port))
    
        JobEngine.connect(in_q, out_q)

        require('loader')

        while True:
            JobEngine.run()
            Scheduler.run()
            if JobEngine.is_waiting() or Scheduler.is_waiting():
                next
            else:
                break
    finally:        
        cleanup()

if __name__ == '__main__':
    main()

