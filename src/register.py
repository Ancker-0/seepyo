from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

from toolbox import RegArrays

class Register :
    def __init__(self, ego):
        super().__init__()
        self.val = RegArrays(Bits(32), 32, ego)
        self.dependence = RegArrays(Bits(32), 32, ego)

    def update(self, update_pos, update_val, update_id):
        self.val[update_pos] = update_val
        self.dependence[update_pos] = update_id

    def show(self):
        for i in range(32):
            log("Register[{}] = {}, dependence = {}", Bits(32)(i), self.val[i], self.dependence[i])