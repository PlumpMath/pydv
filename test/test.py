@entity()
def foo3(self):
    @action(self)
    def build(self):
        yield from cmd("echo aaa")

@entity()
def foo(self):
    @action(self)
    def build(self):
        yield from cmd('echo bbb')

@namespace()
def comp(self):
    @action(self)
    def aaaaa(self):
        logger.info(self)

@entity()
def foo2(self):
    self.need(foo3)
    self.mixin(comp)
    @action(self)
    def build(self):
        yield from self.aaaaa()

@suite()
def aaa(self):
    @test(self)
    def bar(self):
        self.need(foo)
        self.need(foo2)

    @test(self)
    def bar2(self):
        self.clone(self.parent.bar)

@suite()
def aaa(self):
    @test(self)
    def bar1(self):
        self.aaa = 'bbb'
        self.need(foo)
        self.need(foo2)

@event.subscribe('dvpy_done')
def body():
    logger.info('finished')
