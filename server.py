import asyncio
import socket
import marshal
import os
from os import path
from logger import logger, FORMAT, get_level
import logging
#import queue

in_q  = None
out_q = None

class AgentServerProtocal(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = marshal.loads(data)
        logger.debug(message)
        out_q.put(message)
        #self.transport.close()

def start_agent_server(_out_q, _in_q, out_dir, verbose):

    global in_q, out_q

    in_q = _in_q
    out_q = _out_q

    logger.setLevel(get_level(verbose))

    server_log = path.abspath(path.join(out_dir, 'agent_server.log'))
    try:
        os.makedirs(path.dirname(server_log))
    except Exception as e:
        pass
    if path.exists(server_log):
        os.rename(server_log, (server_log+'.bak'))
    fh = logging.FileHandler(server_log)
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(get_level(verbose))

    logger.addHandler(fh)
    
    loop = asyncio.get_event_loop()

    server_host = socket.gethostname()
    server_ip = socket.gethostbyname(server_host)
    
    coro = loop.create_server(AgentServerProtocal, server_ip)
    server = loop.run_until_complete(coro)

    _, server_port = server.sockets[0].getsockname()

    logger.info('agent server started on {}:{}'.format(server_host, server_port))    

    out_q.put((server_host, server_port))

    loop.run_forever()

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

#start_agent_server(queue.Queue(), queue.Queue())
