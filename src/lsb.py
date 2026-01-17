from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

from src.const import INST_WIDTH, LSB_SIZE
from src.instruction import Inst
from toolbox import RegArrays

class LSB(Module):
    def __init__(self):
        super().__init__(ports = {
            "p_opid": Port(Bits(32)),
            "p_rs1": Port(Bits(32)),
            "p_rs2": Port(Bits(32)),
            "p_imm": Port(Bits(32)),
            "flush_tag": Port(Bits(1)),

            "p_robid": Port(Bits(32)),
            "p_robval": Port(Bits(32)),
        })

        self.size = LSB_SIZE
        self.opid = RegArrays(Bits(32), LSB_SIZE, self)
        self.Vj = RegArrays(Bits(32), LSB_SIZE, self)
        self.Vk = RegArrays(Bits(32), LSB_SIZE, self)
        self.Qj = RegArrays(Bits(32), LSB_SIZE, self)
        self.Qk = RegArrays(Bits(32), LSB_SIZE, self)
        self.rd_robid = RegArrays(Bits(32), LSB_SIZE, self)
        self.done = RegArrays(Bits(1), LSB_SIZE, self)
        self.imm = RegArrays(Bits(32), LSB_SIZE, self)

    def clean(self, Id):
        self.opid[Id] = Bits(32)(0)
        self.Vj[Id] = Bits(32)(0)
        self.Vk[Id] = Bits(32)(0)
        self.Qj[Id] = Bits(32)(0)
        self.Qk[Id] = Bits(32)(0)
        self.rd_robid[Id] = Bits(32)(0)
        self.done[Id] = Bits(1)(0)
        self.imm[Id] = Bits(32)(0)

    def log(self):
        log("------- LSB log start -------")
        for i in range(self.size):
            log("Op = ${}$, Vj = {}, Vk = {}, Qj = {}, Qk = {}, imm = {}, rd_robid = {}, Done = {}",
                self.opid[i], self.Vj[i], self.Vk[i], self.Qj[i], self.Qk[i], self.imm[i], self.rd_robid[i], self.done[i])
        log("------- LSB log end -------")
    
    def avail(self):
        ret = Bits(1)(0)
        for i in range(self.size):
            ret = ret | (self.opid[i] == Bits(32)(0))
        return ret

    @module.combinational
    def build(self):
        flush = self.flush_tag.valid()
        with Condition(flush):
            for i in range(self.size):
                self.clean(i)
            for port in self.ports:
                with Condition(port.valid()):
                    port.pop()
        with Condition(~flush):
            with Condition(self.p_opid.valid()):
                pass

            # done things for ROB
            with Condition(self.p_robid.valid()):
                rob_id = self.p_robid.pop()
                rob_value = self.p_robval.pop()
                for i in range(self.size):
                    with Condition(self.opid[i] != Bits(32)(0)):
                        with Condition(self.Qj[i] == rob_id):
                            self.Vj[i] = rob_value
                            self.Qj[i] = Bits(32)(0)
                        with Condition(self.Qk[i] == rob_id):
                            self.Vk[i] = rob_value
                            self.Qk[i] = Bits(32)(0)

        self.log()