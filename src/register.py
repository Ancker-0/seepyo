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
        log("RF update: pos = {}, val = {}, id = {}", update_pos, update_val, update_id)
        with Condition(update_pos != Bits(32)(0)):
            # When update_id != 0 (new instruction setup), preserve the current value
            # This ensures that when a new instruction targets the same register as a
            # committing instruction, the committing instruction's result is preserved.
            # The actual value will be set by the commit logic or the ALU result.
            with Condition(update_id != Bits(32)(0)):
                # New instruction setup: only update dependence, preserve current value
                self.dependence[update_pos] = update_id
            with Condition(update_id == Bits(32)(0)):
                # Commit or special case: update both value and dependence
                self.val[update_pos] = update_val
                self.dependence[update_pos] = update_id

    def update_noval(self, update_pos, update_id):
        log("RF update: pos = {}, id = {}", update_pos, update_id)
        with Condition(update_pos != Bits(32)(0)):
            self.dependence[update_pos] = update_id

    def update_value_only(self, update_pos, update_val):
        """Update only the register value, not the dependence. Used when a new instruction
        targets the same register as a committing instruction."""
        log("RF update value only: pos = {}, val = {}", update_pos, update_val)
        with Condition(update_pos != Bits(32)(0)):
            self.val[update_pos] = update_val

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