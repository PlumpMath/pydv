from entity import EntityBase
from namespace import Namespace
from copy import copy
from entity import action
from types import GeneratorType
from visitor import join, spawn

class Suite(Namespace):

    tests = {}

    def __init__(self, body, parent=None):
        super(Suite, self).__init__(body, parent)

def suite(parent=None):
    def f(body):
        s = Suite(body, parent)
        Namespace.suites[s.fullname] = s
        if parent:
            parent.add(body.__name__, s)
        return s
    return f

class Test(EntityBase):

     def __init__(self, body, parent=None):
         super(Test, self).__init__(body, parent)
         @action(self)
         def run():
             pass

def test(parent=None):
    def f(body):
        t = Test(body, parent)
        Suite.tests[t.fullname] = t
        if parent:
            if type(parent) == Suite:
                parent.add(body.__name__, t)
            else:
                raise Exception('attempt to define test {} in non-suite {}'.format(body.__name__, parent))
        return t
    return f

def run_test(*ts, actions=[]):
    @join
    def body(self):
        for tn in ts:
            ps = tn.split('.')
            for sn in ps:
                if sn in Namespace.suites:
                    Namespace.suites[sn]()
            @spawn(self)
            def b(tn=tn):
                if tn in Suite.tests:
                    t = Suite.tests[tn]()
                    res = t.build()
                    if type(res) == GeneratorType:
                        res = yield from res
                    return res
                else:
                    raise Exception('cannot find test {}'.format(tn))
