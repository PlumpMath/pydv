@entity()
def foo3(self):
    @action(self)
    def build():
        yield from cmd("echo aaaa")

@entity()
def foo(self):
    @action(self)
    def build():
        yield from cmd('echo bbbb')

@entity()
def foo2(self):
    self.need(foo3())
    @action(self)
    def build():
        pass

@entity()
def bar(self):
    self.need(foo())
    self.need(foo2())
    @action(self)
    def build():
        pass

