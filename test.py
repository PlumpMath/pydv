from entity import EntityBase, Entity
from namespace import Namespace
from copy import copy
from entity import action
from types import GeneratorType
from visitor import join, spawn
from pyparsing import Forward, Combine, Regex, Keyword, Word, QuotedString, alphas, alphanums, quotedString, lineEnd
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
            yield from self.build()

    def clone(self, p):
        p().body(self)

    def my_suite(self):
        return self.parent

    def need(self, *ntts):
        for n in ntts:
            if type(n) != Entity:
                raise Exception('attempt to need a non-entity {}:{}'.format(type(n), n))
            super(Test, self).need(n)

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
        try:
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
                            reg = re.compile(nv)
                            return re.search(reg, av)
                        else:
                            reg = re.compile(nv)
                            return not re.search(reg, av)
            else:
                return False
        except Exception as e:
            print(e)
            return False
    return f

attr   = Regex('[^=!\s]+')
value  = Regex('[^=!~\s\(\)\&\|\"\']+') | QuotedString('"') | QuotedString("'")
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

def get_test(*ts, where=None):
    wp = None
    if where:
        wp = parse_selector(where)[0]
    reg = re.compile("all")
    res = []
    for tn in ts:
        ps = tn.split('.')
        st = []
        for sn in ps:
            st.append(sn)
            nsn = '.'.join(st)
            if nsn in Namespace.namespaces:
                Namespace.namespaces[nsn]()
        if re.search(reg, tn):
            ntn = re.sub(reg, '[^\.]+', tn)
            nreg = re.compile(ntn)
            for tnn in Suite.tests:
                if re.fullmatch(nreg, tnn):
                    t = Suite.tests[tnn]()
                    if wp and not wp(t):
                        pass
                    else:
                        res.append(t)
        else:
            if tn in Suite.tests:
                t = Suite.tests[tn]()
                if wp and not wp(t):
                    pass
                else:
                    res.append(t)
            else:
                raise Exception('cannot find test {}'.format(tn))
    return res
                

def run_test(*ts, action=None, where=None):
    if action == None:
        action=['run']
    nts = get_test(*ts, where=where)
    @join
    def body(self):
        for t in nts:
            @spawn(self)
            def b(t=t):
                try:
                    res = None
                    for a in action:
                        res = getattr(t, a)()
                        if type(res) == GeneratorType:
                            res = yield from res
                        Test.test_status[t.fullname] = 'passed'
                    return res
                except Exception as e:
                    Test.test_status[t.fullname] = 'failed'
                    raise e
    yield from body()
