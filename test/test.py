@entity()
def foo3(self):
    @action(self)
    def build():
        yield from cmd("echo aaa")

@entity()
def foo(self):
    @action(self)
    def build():
        yield from cmd('echo bbb')

@entity()
def foo2(self):
    self.need(foo3)

@suite()
def aaa(self):
    @test(self)
    def bar(self):
        self.need(foo)
        self.need(foo2)

@event.subscribe('dvpy_done')
def body():
    logger.info('finished')
