from visitor import visitor
from scheduler import Scheduler
from gcfengine import GCFEngine
import socket
import marshal
import hashlib
from logger import logger
from os import path
from time import time
from threading import Timer

class JobEngine:

    agent_visitor = {}
    visitor_agent = {}

    idle_agents = set()
    reused_agents = set()

    agent_count = 0
    agent_md5 = hashlib.md5()

    agent_status = {}
    agent_time_out = 600
    time_out = 60
    timer = None

    max_cmds = 1
    cmds = []
    running_cmds = {}
    pending_cmds = {}

    jobengine_visitor = None

    input_q = None
    output_q = None

    out_dir = None

    @classmethod
    def connect(cls, in_q, out_q):
        cls.input_q = in_q
        cls.output_q = out_q

    @classmethod
    def push_cmd(cls, v, cmd_spec):
        logger.debug("push command {}".format(cmd_spec))
        cls.cmds.append((v, cmd_spec))

    @classmethod
    def run(cls):
        if cls.jobengine_visitor:
            Scheduler.wake(cls.jobengine_visitor)
        else:
            cls.timer = Timer(cls.time_out, cls.agent_checker, args=(cls,))
            cls.timer.start()
            @visitor
            def body():
                try:
                    while True:
                        cls.process_msg()
                        while len(cls.cmds) > 0 and (len(cls.pending_cmds) + len(cls.running_cmds)) < cls.max_cmds:
                            v, cmd_spec = cls.cmds.pop()
                            agent_id = cls.get_agent(v);
                            cmd_spec['agent_id'] = agent_id
                            cls.pending_cmds[agent_id] = cmd_spec
                        yield from Scheduler.sleep()
                except Exception as e:
                    logger.error(e)
            cls.jobengine_visitor = body

    @classmethod
    def get_agent(cls, v):
        if v in cls.visitor_agent:
            return cls.visitor_agent[v]
        else:
            if len(cls.idle_agents) > 0:
                agent_id = cls.idle_agents.pop()
                cls.reused_agents.add(agent_id)
                vv = cls.agent_visitor[agent_id]
                del cls.visitor_agent[vv]
                del cls.agent_visitor[agent_id]
                del cls.agent_status[agent_id]
            else:
                cls.agent_count += 1
                cls.agent_md5.update(bytes(cls.agent_count))
                agent_id = cls.agent_md5.hexdigest()
                GCFEngine.spawn_agent(agent_id)
            cls.visitor_agent[v] = agent_id
            cls.agent_visitor[agent_id] = v
            cls.agent_status[agent_id] = time()
            return agent_id

    @classmethod
    def cleanup(cls):
        if cls.timer:
            cls.timer.cancel()
        for agent_id in cls.agent_visitor:
            GCFEngine.kill_agent(agent_id)

    @classmethod
    def process_msg(cls):
        while cls.input_q.qsize() > 0:
            msg = cls.input_q.get()
            cmd = msg['cmd']
            cases = {'heart_beat'    : cls.heart_beart,
                     'require_cmd'   : cls.require_cmd,
                     'update_status' : cls.update_status,
                     'cmd_done'      : cls.cmd_done}
            cases[cmd](cls, msg)

    @classmethod
    def is_waiting(cls):
        #print("running_cmds {}".format(cls.running_cmds))
        #print("pending_cmds {}".format(cls.pending_cmds))
        #print("cmds {}".format(cls.cmds))
        #print("agent_visitor {}".format(cls.agent_visitor))
        #print("visitor_agent {}".format(cls.visitor_agent))
        #print("reused_agents{}".format(cls.reused_agents))
        return (len(cls.running_cmds) > 0 or
                len(cls.pending_cmds) > 0 or
                len(cls.cmds) > 0 or
                len(cls.agent_visitor) > 0 or
                len(cls.visitor_agent) > 0 or
                len(cls.reused_agents) > 0)

    def require_cmd(cls, data):
        agent_id = data['agent_id']
        agent_host = data['agent_host']
        agent_port = data['agent_port']
        cmd_spec = {'cmd' : 'terminate'}
        if agent_id in cls.pending_cmds:
            cmd_spec = cls.pending_cmds[agent_id]
            cmd_spec['logfile'] = path.join(cls.out_dir, 'cmds', agent_id)
            del cls.pending_cmds[agent_id]
            if agent_id in cls.reused_agents:
                cls.reused_agents.remove(agent_id)
            cls.running_cmds[agent_id] = cmd_spec
       
        out_data = marshal.dumps(cmd_spec)
        re_try = 10
        while True:
            try:
                s = socket.socket()
                s.connect((agent_host, agent_port))
                try:
                    s.send(out_data)
                finally:
                    s.close()
                break
            except Exception as e:
                re_try -= 1
                logger.warning(str(e))
                if re_try > 0:
                    pass
                else:
                    raise e

        if agent_id not in cls.running_cmds and agent_id not in cls.reused_agents:
            if agent_id in cls.idle_agents:
                cls.idle_agents.remove(agent_id)
            if agent_id in cls.agent_visitor:
                GCFEngine.kill_agent(agent_id)
                v = cls.agent_visitor[agent_id]
                del cls.visitor_agent[v]
                del cls.agent_visitor[agent_id]
                del cls.agent_status[agent_id]

    def heart_beart(cls, data):
        #print(data)
        agent_id = data['agent_id']
        cls.agent_status[agent_id] = time()

    def agent_checker(cls):
        for agent_id in cls.agent_status:
            if (time() - cls.agent_status[agent_id]) > cls.agent_time_out:
                if agent_id in cls.running_cmds:
                    GCFEngine.kill_agent(agent_id)
                    cmd_spec = cls.running_cmds[agent_id]
                    v = cls.agent_visitor[agent_id]
                    del cls.visitor_agent[v]
                    del cls.agent_visitor[agent_id]
                    del cls.agent_status[agent_id]
                    del cls.running_cmds[agent_id]
                    cls.push_cmd(v, cmd_spec)
        cls.timer = Timer(cls.time_out, cls.agent_checker, args=(cls,))
        cls.timer.start()

    def update_status(cls, data):
        pass

    def cmd_done(cls, data):
        #print(data)
        agent_id = data['agent_id']
        cmd_spec = cls.running_cmds[agent_id]
        cmd_spec['exitcode'] = data['exitcode']
        cmd_spec['errmsg']   = data['errmsg']
        del cls.running_cmds[agent_id]
        cls.idle_agents.add(agent_id)
        Scheduler.wake(cls.agent_visitor[agent_id])
        
