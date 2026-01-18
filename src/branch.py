from assassyn.frontend import *
from const import PREDICTOR_SIZE
from toolbox import RegArrays

class Predictor(Module):
    def __init__(self):
        self.size = PREDICTOR_SIZE
        self.table = RegArrays(Bits(2), self.size, self, [1 for _ in range(self.size)])
        super().__init__(ports={
            "p_PC": Port(Bits(32)),
            "p_accept": Port(Bits(1)),
        })
    
    @module.combinational
    def build(self):
        with Condition(self.p_PC.valid()):
            PC, accept = self.pop_all_ports(True)
            idx = (PC >> Bits(32)(2)) % Bits(32)(self.size)
            idle = accept.select(self.table[idx] == Bits(2)(3), self.table[idx] == Bits(2)(0))
            with Condition(~idle):
                self.table[idx] = self.table[idx] + accept.select(Bits(2)(1), Bits(2)(3))

    def branch_predict(self, PC: Bits, label: Bits):
        idx = (PC >> Bits(32)(2)) % Bits(32)(self.size)
        state = self.table[idx]
        return (state >> Bits(2)(1)).bitcast(Bits(1))
        # return Int(32)(4) > label.bitcast(Int(32))