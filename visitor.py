from types import GeneratorType
from scheduler import Scheduler

class Visitor:
    
    def __init__(self, body):
        self.name = body.__name__
        def f(*args, **kargs):
            try:
                res = body(*args, **kargs)
                if type(res) == GeneratorType:
                    res = yield from res
            except Exception as e:
                self.exception = e
            #    raise e
            finally:
                for i in self.waiters:
                    Scheduler.wake(i)
                self.done = True
            return res
        self.body = f
        self.exception = None
        self.waiters = set()
        self.done = False
        self.initialized = False
        self.cwd = None
        Scheduler.add(self)
        
    def __call__(self, *args, **kargs):
        if not self.initialized:
            self.initialized = True
            self.body = self.body(*args, **kargs)
        return self.body
    
    def add_waiter(self, v):
        self.waiters.add(v)

    def remove_waiter(self, v):
        self.waiters.remove(v)

    def resume(self):
        Scheduler.current = self
        try:
            next(self())
        except StopIteration as e:
            pass
        #except Exception as e:
        #    self.exception = e
        #    raise e
        
def visitor(body):
    return Visitor(body)


class Joiner:

    def __init__(self, body):
        self.children = set()
        body(self)

    def __call__(self):
        yield from self.wait_for_children()

    def add_child(self, v):
        self.children.add(v)
        v.add_waiter(Scheduler.current)

    def wait_for_children(self):
        def all_done():
            for v in self.children:
                if not v.done:
                    return False
            return True
        while not all_done():
            yield from Scheduler.sleep()
        es = []
        for v in self.children:
            if v.exception:
                es.append(v.exception)
        if len(es) > 0:
            raise Exception(es)
    
def join(body):
    return Joiner(body)

def spawn(parent=None):
    def f(body):
        @visitor
        def ff():
            res = body()
            if type(res) == GeneratorType:
                yield from res
            return res
        if parent:
            parent.add_child(ff)
    return f


