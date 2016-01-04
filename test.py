from entity import EntityBase
from namespace import Namespace
from copy import copy
from entity import action
from types import GeneratorType
from visitor import join, spawn
from pyparsing import Forward, Group, Keyword, Word, QuotedString, alphas, alphanums, quotedString, lineEnd
import re

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

     def clone(self, p):
         p().body(self)

     def my_suite(self):
         return self.parent

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

def eval_simple(a, o, v):
    def f(self):
        if hasattr(self, a):
            nv = str(v)
            av = str(getattr(self, a))
            if o == '==':
                return av == nv
            else:
                if o == '!=':
                    return not (av == nv)
                else:
                    if o == '=~':
                        reg = reg.complie(nv)
                        return re.search(reg, av)
                    else:
                        reg = reg.complie(nv)
                        return not re.search(reg, av)
        else:
            return False
    return f

attr   = Word(alphas)
value  = Word(alphanums) | QuotedString('"') | QuotedString("'")
op     = Keyword('==') | Keyword('!=') | Keyword('=~') | Keyword('!~')
simple = (attr + op + value).setParseAction(lambda s, l, t: eval_simple(*t.asList()))
expr   = Forward()
single = ('(' + expr + ')').setParseAction(lambda s, l, t: t[1]) | simple
comb   = ((single + '&' + expr).setParseAction(lambda s, l, t: (lambda self: t[0](self) and t[2](self))) |
          (single + '|' + expr).setParseAction(lambda s, l, t: (lambda self: t[0](self) or  t[2](self))))
expr <<= comb | single

parser = expr + lineEnd

def parse_selector(s):
    try:
        p = parser.parseString(s)
    except Exception as e:
        raise Exception("failed at parse '{}': {}".format(s, e))
    return p

def run_test(*ts, action=None, where=None):
    if action == None:
        action=['build']
    wp = None
    if where:
        wp = parse_selector(where)[0]
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
                        if wp:
                            if not wp(t):
                                return None
                        res = None
                        for a in action:
                            res = getattr(t, a)()
                            if type(res) == GeneratorType:
                                res = yield from res
                            Test.test_status[tn] = 'passed'
                        return res
                    else:
                        raise Exception('cannot find test {}'.format(tn))
                except Exception as e:
                    Test.test_status[tn] = 'failed'
                    raise e
    yield from body()
