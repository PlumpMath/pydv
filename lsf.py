from subprocess import Popen, PIPE
import shlex
from os import path 

class LSF:

    def __init__(self, host, port, out_dir, verbose):
        self.agent_ids = {}
        self.host = host
        self.port = port
        self.out_dir = out_dir
        self.verbose = verbose

    def spawn_agent(self, agent_id):
        d = path.dirname(__file__)
        #self.agent_ids[agent_id] = p

    def kill_agent(self, agent_id):
        if agent_id in self.agent_ids:
            p = self.agent_ids[agent_id]
            p.terminate()
            del self.agent_ids[agent_id]
