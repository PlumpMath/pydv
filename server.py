import asyncio
import socket
import marshal
#import queue

in_q  = None
out_q = None

class AgentServerProtocal(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = marshal.loads(data)
        #print(message)
        out_q.put(message)
        #self.transport.close()

def start_agent_server(_out_q, _in_q):

    global in_q, out_q

    in_q = _in_q
    out_q = _out_q
    
    loop = asyncio.get_event_loop()

    server_host = socket.gethostname()
    server_ip = socket.gethostbyname(server_host)
    
    coro = loop.create_server(AgentServerProtocal, server_ip)
    server = loop.run_until_complete(coro)

    _, server_port = server.sockets[0].getsockname()
    
    out_q.put((server_host, server_port))

    loop.run_forever()

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

#start_agent_server(queue.Queue(), queue.Queue())
