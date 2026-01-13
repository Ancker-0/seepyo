from assassyn.frontend import *
from fetch import INST_WIDTH

class Memory(Module):
    def __init__(self):
        super().__init__(
            ports = {
                'rd': Port(Bits(5)),
                'read': Port(Bits(1)),
            })

    @module.combinational
    def build(self):
        rd = self.rd.pop()
        isRead = self.read.pop()