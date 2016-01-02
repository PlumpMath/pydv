from graph import Node, needgraph, actiongraph
from visitor import visitor, join, spawn
from scheduler import Scheduler
from types import GeneratorType
from job import JobEngine
from logger import logger
from namespace import Namespace
from copy import copy
import types

class EntityBase:
    
    ntts = {}
    
    @classmethod
    def register_entity(cls, name, ntt):
        if name in cls.ntts:
            raise Exception("attempt to redefine an entity " + name)
        else:
            cls.ntts[name] = ntt
            
    def __init__(self, body, parent=None):
        self.name = body.__name__
        self.fullname = self.name
        if parent:
            self.fullname = str(parent) + '.' + self.name
        self.body = body
        self.parent = parent
        self.needs = set()
        self.initialized = False
        self.node = Node(self.name)
        self.node.ntt = self
        self.node.color = 'white'
        self.node.waiters = set()
        self.node.waiter_nodes = set()
        self.node.wait_on = set()
        needgraph.add_node(self.node)
        @action(self)
        def build(self):
            pass
        EntityBase.register_entity(self.fullname, self)
        
    def add(self, name, action, org_action=None):
        self.__dict__[name] = action
        return action

    def mixin(self, ns):
        if not isinstance(ns, Namespace):
            raise Exception("attempt to maxin in non-namspace {}".format(ns))
        for n in ns().ns:
            self.__dict__[n] = types.MethodType(ns.ns[n], self)
    
    def initialize(self):
        if not self.initialized:
            self.initialized = True
            self.body(self)
            
    def __call__(self):
        self.initialize()
        return self

    def __str__(self):
        return self.fullname

    def need(self, ntt):
        self.needs.add(ntt())
        needgraph.add_edge(self.node, ntt.node)

    def add_waiter(self, n):
        self.node.waiters.add(Scheduler.current)
        self.node.waiter_nodes.add(n)

    def wake_waiters(self):
        for v in self.node.waiters:
            Scheduler.wake(v)

    def build_need(self):
        n = self.node
        cv = Scheduler.current
        if n.color == 'black':
            return
        
        sg = needgraph.subgraph(n)
        for i in self.needs:
            if i.node.color == 'gray':
                i.add_waiter(n)
                n.wait_on.add(i.node)
                sg.remove_node(i.node)
                ssg = needgraph.subgraph(i.node)
                for j in ssg.nodes_iter():
                    sg.remove_node(j)
                    
        for i in sg.nodes_iter():
            if not i.color == 'black':
                i.color = 'gray'

        ns = set()
        def collect_nodes():
            for i in sg.nodes_iter():
                if sg.out_degree(i) == 0 and not i.color == 'black':
                    ns.add(i.ntt)
        collect_nodes()
        try:
            while len(ns) > 0:
                @join
                def body(s):
                    for i in ns:
                        @spawn(s)
                        def f(ii=i):
                            try:
                                yield from ii.build()
                            finally:
                                ii.node.color = 'black'
                                ns.remove(ii)
                                if sg.has_node(ii.node):
                                    sg.remove_node(ii.node)
                yield from body()
                collect_nodes()
            
            while len(n.wait_on) > 0:
                yield from Scheduler.sleep()

        except Exception as e:
            cv.exception = e
            for i in sg.nodes_iter():
                i.color = 'black'
                for j in i.waiter_nodes:
                    j.wait_on.remove(i)
                for v in i.waiters:
                    v.exception = cv.exception
                    Scheduler.wake(v)

        n.color = 'black'
            
        for i in n.waiter_nodes:
            i.wait_on.remove(n)

        for v in n.waiters:
            if cv.exception:
                v.exception = cv.exception
            Scheduler.wake(v)
            
        n.waiters.clear()
        n.waiter_nodes.clear()

        if cv.exception:
            raise cv.exception


class Entity(EntityBase):
    
    def __init__(self, body, parent=None):
        super(Entity, self).__init__(body, parent)


def entity(parent=None):
    def f(body):
        ntt = Entity(body, parent=parent)
        if parent:
            if type(parent) == Namespace:
                 parent.add(body.__name__, ntt)
            else:
                 raise Exception('attempt to define entity {} in non-component {}'.format(body.__name__, parent))
        return ntt
    return f

def action(parent=None):
    def f(a):
        def na(*args, **kargs):
            fn = a.__name__
            if parent:
                fn = str(parent) + '.' + fn
            logger.info('-> running action {}'.format(fn))
            
            try:    
                if a.__name__ == 'build':
                    if parent:
                        yield from parent.build_need()
                res = a(*args, **kargs)
                if type(res) == GeneratorType:
                    res = yield from res
                logger.info('<- action {} passed'.format(fn))
                return res
            except Exception as e:
                logger.error('<- action {} failed'.format(fn))
                raise e
        if parent:
            parent.add(a.__name__, types.MethodType(na, parent), na)
            if a.__name__ == 'build':
                def nna(*args, **kargs):
                    fn = 'build_self'
                    if parent:
                        fn = str(parent) + '.' + fn
                    logger.info('-> running action {}'.format(fn))
                    try:
                        res = a(*args, **kargs)
                        if type(res) == GeneratorType:
                            res = yield from res
                        logger.info('<- action {} passed'.format(fn))
                        return res
                    except Exception as e:
                        logger.info('<- action {} failed'.format(fn))
                        raise e
                parent.add('build_self', types.MethodType(nna, parent))
        return na
    return f

def cmd(*args):
    cmd_spec = {}
    cmd_spec['cmd'] = ' '.join(args)
    v = Scheduler.current
    if v.cwd:
        cmd_spec['dir'] = v.cwd
    JobEngine.push_cmd(v, cmd_spec)
    yield from Scheduler.sleep()
    exitcode = cmd_spec['exitcode']
    if exitcode == 0:
        logger.info("> command '{}' passed".format(cmd_spec['cmd']))
    else:
        errmsg = cmd_spec['errmsg'] + (" with exitcode {}".format(exitcode))
        logger.error("> command '{}' failed: {}".format(cmd_spec['cmd'], errmsg))
        raise Exception(errmsg)

def dir(p):
    v = Scheduler.current
    v.cwd = p
