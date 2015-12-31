from optparse import OptionParser
import socket
from threading import Timer, Thread
import marshal
import asyncio
from queue import Queue
import os
from subprocess import Popen, PIPE
import shlex
import signal

host = None
port = None
agent_id = None

time_out = 60

cmd_q = Queue()

def talk_to_server(data):
    re_try = 10
    while True:
        try:
            s = socket.socket()
            s.connect((host, port))
            try:
                s.send(data)
            finally:
                s.close()
                pass
            break
        except Exception as e:
            print(e)
            re_try -= 1
            if re_try > 0:
                pass
            else:
                raise e


def send_heart_beat():
    data = {'cmd' : 'heart_beat',
            'agent_id' : agent_id}
    bs = marshal.dumps(data)
    re_try = 10
    while True:
        try:
            talk_to_server(bs)
            break
        except Exception as e:
            re_try -= 1
            print(str(e))
            if re_try > 0:
                pass
            else:
                cleanup()
                exit(-1)
    Timer(time_out, send_heart_beat).start()
    

class AgentProtocal(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        msg = marshal.loads(data)
        cmd_q.put(msg)
        #self.transport.close()

server_host = None
server_port = None
def start_server(loop):
    
    global server_host, server_port
    
    #loop = asyncio.get_event_loop()

    server_host = socket.gethostname()
    server_ip = socket.gethostbyname(server_host)

    coro = loop.create_server(AgentProtocal, server_ip)
    server = loop.run_until_complete(coro)

    _, server_port = server.sockets[0].getsockname()

    cmd_q.put(True)
    
    loop.run_forever()

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
    
def get_cmd():
    data = {'cmd' : 'require_cmd',
            'agent_id' : agent_id,
            'agent_host' : server_host,
            'agent_port' : server_port}
    bs = marshal.dumps(data)
    talk_to_server(bs)
    cmd_spec = cmd_q.get()
    return cmd_spec

def send_status(msg):
    data = {'cmd' : 'update_status',
            'agent_id' : agent_id,
            'msg' : msg}
    bs = marshal.dumps(data)
    talk_to_server(bs)

def cmd_done(exitcode, err):
    data = {'cmd' : 'cmd_done',
            'agent_id' : agent_id,
            'exitcode' : exitcode,
            'errmsg' : err}
    bs = marshal.dumps(data)
    talk_to_server(bs)

inferior_process = None
server_thread = None

def cleanup():
    if inferior_process:
        inferior_process.terminate()
    #if server_thread:
    #    server_thread.kill()

def handler(signum, frame):
    if inferior_process:
        inferior_process.terminate()
    exit(-1)

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)
 
def run():
    global inferior_process
    global server_thread

    Timer(time_out, send_heart_beat).start()

    loop = asyncio.get_event_loop()
    server_thread = Thread(target=start_server, args=(loop,)).start()

    cmd_q.get()

    cwd = os.getcwd()
    
    while True:
        try:
            os.chdir(cwd)
            cmd_spec = get_cmd()
            print(cmd_spec)
            if not cmd_spec:
                next
            cmd = cmd_spec['cmd']
            if cmd == 'terminate':
                break
            if 'dir' in cmd_spec:
                path = cmd_spec['dir']
                os.chdir(path)
            args = shlex.split(cmd)
            p = Popen(args, shell=True, stdout=PIPE, stderr=PIPE)
            inferior_process = p
            out, err = p.communicate()
            print((out, err))
            exitcode = p.returncode
            cmd_done(exitcode, err.decode())
        except Exception as e:
            send_status(str(e))
            pass

    cleanup()        
    
def main():

    global host, port, agent_id
    
    p = OptionParser()
    p.add_option('-m', '--host', dest='host',
                 help='specify host name')
    p.add_option('-p', '--port', dest='port',
                 help='specify port')
    p.add_option('-i', '--id', dest='id',
                 help='specify id name')
    
    (options, args) = p.parse_args()

    host = options.host
    port = int(options.port)
    agent_id = options.id

    run()

if __name__ == '__main__':
    main()
