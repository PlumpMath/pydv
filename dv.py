#!/usr/bin/env python3.4

from multiprocessing import Process, Queue
from threading import Thread
import asyncio
import signal
from types import GeneratorType
from os import path
import logging
from traceback import extract_tb

from server import start_agent_server
from job import JobEngine
from scheduler import Scheduler
from entity import entity, action, cmd
from visitor import visitor, join, spawn
from local import Local
from gcfengine import GCFEngine
from utils import require, get_ns
from option import args_parse
from logger import logger
import event
from test import run_test, Test

server_p = None

def cleanup():
    if server_p:
        server_p.terminate()
    JobEngine.cleanup()
    logging.shutdown()

def handler(signum, frame):
    cleanup() 
    exit(-1) 

#signal.signal(signal.SIGINT, handler)
#signal.signal(signal.SIGTERM, handler)

def main():

    global server_p

    # parsing arguments
    (opts, args) = args_parse()

    in_q  = Queue()
    out_q = Queue()

    logger.info('running dv.py')
    # start agent server
    #loop = asyncio.get_event_loop()
    server_p = Process(target=start_agent_server, args=(in_q, out_q, path.abspath(opts.out_dir), opts.verbose,))
    #server_p = Thread(target=start_agent_server, args=(loop, in_q, out_q,))
    server_p.start()

    try:
        # waiting for server started
        host, port = in_q.get()

        #logger.info("agent server started on {}:{}".format(host, port))

        # set gcf engine    
        GCFEngine.set_imp(Local(host, port, path.abspath(opts.out_dir), opts.verbose))
    
        # config job engine
        JobEngine.connect(in_q, out_q)
        JobEngine.out_dir = path.abspath(opts.out_dir)
        logger.info('max agents = {}'.format(opts.max_agents))
        JobEngine.max_cmds = int(opts.max_agents)

        # load files
        require('loader')

        # evaluate experssions
        @visitor
        def top():
            @join
            def body(self):
                if opts.expr:
                    for e in opts.expr:
                        @spawn(self)
                        def body(ee=e):
                            res = eval(ee, get_ns(), get_ns())
                            if type(res) == GeneratorType:
                                yield from res
                            return res
                if opts.test:
                    @spawn(self)
                    def body():
                        res = run_test(*opts.test)
                        if type(res) == GeneratorType:
                            yield from res
                        return res
            yield from body()

        # run
        while True:
            JobEngine.run()
            Scheduler.run()
            if JobEngine.is_waiting() or Scheduler.is_waiting():
                next
            else:
                break
        for t in Test.test_status:
            if Test.test_status[t] == 'passed':
                logger.info("test '{}' passed".format(t))
            else:
                logger.error("test '{}' failed".format(t))
        if top.exception:
            def print_exception(e, indent=0):
                if isinstance(e, Exception):
                    for l in extract_tb(e.__traceback__):
                        logger.debug((" "*indent)+str(l))
                if not isinstance(e, Exception):
                    logger.error((" "*indent)+str(e))
                    return
                for i in e.args:
                    if not isinstance(i, list):
                        i = [i]
                    for j in i:
                        print_exception(j, indent+2)
            print_exception(top.exception)
            logger.error('dv.py failed')
            #raise top.exception
        else:
            logger.info('dv.py passed')
    finally:
        event.notify('dvpy_done')
        cleanup()

if __name__ == '__main__':
    main()

