from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

from toolbox import RegArrays

class Register(Module):
    def __init__(self):
        super().__init__(ports={})
        self.val = RegArrays(Bits(32), 32, self)
        self.dependence = RegArrays(Bits(32), 32, self)

    def update(self, update_pos, update_val, update_id):
        self.val[update_pos] = update_val
        self.dependence[update_pos] = update_id

    def clear_dependence(self):
        for i in range(32):
            self.dependence[i] = Bits(32)(0)

    @module.combinational
    def build(self):
        # Initialize all dependence to 0 at startup
        for i in range(32):
            self.dependence[i] = Bits(32)(0)
        # Log to verify initialization
        log("RF initialized: dependence[0]={}, dependence[1]={}, dependence[2]={}, dependence[3]={}",
            self.dependence[0], self.dependence[1], self.dependence[2], self.dependence[3])

    def show(self):
        for i in range(32):
            log("Register[{}] = {}, dependence = {}", Bits(32)(i), self.val[i], self.dependence[i])