from assassyn.frontend import *
from const import WORD_WIDTH, ROB_WIDTH

regTp = Record({
    (0, WORD_WIDTH-1): ('data', Bits),
    (WORD_WIDTH, WORD_WIDTH): ('busy', Bits),
    (WORD_WIDTH+1, WORD_WIDTH): ('busy', Bits),
})

class RegFile(Module):
    def __init__(self):
        super().__init__()
        self.data = RegArray(regTp, 32)

    def build(self):
        return self.data, self.busy, self.robid