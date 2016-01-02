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
        fn = body.__name__
        if parent:
            fn = str(parent) + '.' + fn
        if fn in Namespace.namespaces:
            s = Namespace.namespaces[fn]
            s.add_body(body)
        else:
            s = Suite(body, parent)
            Namespace.namespaces[s.fullname] = s
            if parent:
                parent.add(body.__name__, s)
        return s
    return f

class Test(EntityBase):

     test_status = {}

     def __init__(self, body, parent=None):
         super(Test, self).__init__(body, parent)
         @action(self)
         def run(self):
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
                if sn in Namespace.namespaces:
                    Namespace.namespaces[sn]()
            @spawn(self)
            def b(tn=tn):
                try:
                    if tn in Suite.tests:
                        t = Suite.tests[tn]()
                        res = t.build()
                        if type(res) == GeneratorType:
                            res = yield from res
                        Test.test_status[tn] = 'passed'
                        return res
                    else:
                        raise Exception('cannot find test {}'.format(tn))
                except Exception as e:
                    Test.test_status[tn] = 'failed'
                    raise e
