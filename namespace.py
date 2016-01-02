from copy import copy

class Namespace:

    namespaces = {}

    def __init__(self, body, parent=None):
        self.name = body.__name__
        self.fullname = self.name
        if parent:
            self.fullname = str(parent) + '.' + self.name
        self.bodies = [body]
        self.ns = {}
        self.parent = parent

    def __call__(self):
        self.initialize()
        return self

    def __str__(self):
        return self.fullname

    def add_body(self, b):
        self.bodies.append(b)

    def initialize(self):
        while len(self.bodies) > 0:
            b = self.bodies.pop()
            b(self)

    def add(self, name, body, org_body=None):
        self.__dict__[name] = body
        if org_body:
            self.ns[name] = org_body
        return body

def component(parent=None):
    def f(body):
        fn = body.__name__
        if parent:
            fn = str(parent) + '.' + fn
        if fn in Namespace.namespaces:
            comp = Namespace.namespaces[fn]
            comp.add_body(body)
        else:
            comp = Namespace(body, parent)
            Namespace.namespaces[comp.fullname] = comp
            if parent:
                if type(parent) == Namespace:
                     parent.add(body.__name__, comp)
                else:
                     raise Exception('attempt to define component {} in non-component {}'.format(body.__name__, parent))
        return comp
    return f 

