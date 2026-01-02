from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

from src.const import INST_WIDTH, RS_SIZE
from src.instruction import Inst
from toolbox import RegArrays


class RS(Module):
    def __init__(self):
        super().__init__(ports = {
            "rd": Port(Bits(INST_WIDTH)),
            "rs1": Port(Bits(INST_WIDTH)),
            "rs2": Port(Bits(INST_WIDTH)),
            "imm": Port(Bits(INST_WIDTH)),
            "Type": Port(Bits(INST_WIDTH)),
            "Id": Port(Bits(INST_WIDTH)),
            "flush_tag": Port(Bits(INST_WIDTH)),
            "inst_order_id": Port(Bits(INST_WIDTH)),
        })

        self.size = RS_SIZE
        self.Busy = RegArrays(Bits(1), RS_SIZE, self)
        self.Op_id = RegArrays(Bits(32), RS_SIZE, self)
        self.Vj = RegArrays(Bits(32), RS_SIZE, self)
        self.Vk = RegArrays(Bits(32), RS_SIZE, self)
        self.Qj = RegArrays(Bits(32), RS_SIZE, self)
        self.Qk = RegArrays(Bits(32), RS_SIZE, self)
        self.A = RegArrays(Bits(32), RS_SIZE, self)
        self.Dest = RegArrays(Bits(32), RS_SIZE, self)

    def clean(self, Id):
        self.Busy[Id] = Bits(1)(0)
        self.Op_id[Id] = Bits(32)(0)
        self.Vj[Id] = Bits(32)(0)
        self.Vk[Id] = Bits(32)(0)
        self.Qj[Id] = Bits(32)(0)
        self.Qk[Id] = Bits(32)(0)
        self.A[Id] = Bits(32)(0)

    def log(self):
        log("------- RS log start -------")
        for i in range(self.size):
            log("Busy = {}, Op = ${}$, Vj = {}, Vk = {}, Qj = {}, Qk = {}, A = {}, Dest = {}", self.Busy[i], self.Op_id[i], self.Vj[i], self.Vk[i], self.Qj[i], self.Qk[i], self.A[i], self.Dest[i])
        log("------- RS log end -------")

    @module.combinational
    def build(self, rf):
        flush = self.flush_tag.valid()
        with Condition(flush):
            for i in range(self.size):
                self.clean(i)
            for port in self.ports:
                with Condition(port.valid()):
                    port.pop()
        with Condition(~flush):
            # done things for RS
            with Condition(self.rd.valid()):
                inst = Inst(self.rd.pop(), self.rs1.pop(), self.rs2.pop(), self.imm.pop(), self.Type.pop(), self.Id.pop())
                inst_id = self.inst_order_id.pop()

                once_tag = Bits(1)(1)
                for i in range(self.size):
                    with Condition(once_tag & (~self.Busy[i])): # Type R
                        #now work with different Instruction
                        with Condition(inst.Type == Bits(32)(1)):
                            self.Busy[i] = Bits(1)(1)
                            self.Op_id[i] = inst.id
                            self.Vj[i] = (rf.dependence[inst.rs1] == Bits(32)(0)).select(rf.val[inst.rs1], Bits(32)(0))
                            self.Vk[i] = (rf.dependence[inst.rs2] == Bits(32)(0)).select(rf.val[inst.rs2], Bits(32)(0))
                            self.Qj[i] = (rf.dependence[inst.rs1] == Bits(32)(0)).select(Bits(32)(0), rf.dependence[inst.rs1])
                            self.Qk[i] = (rf.dependence[inst.rs2] == Bits(32)(0)).select(Bits(32)(0), rf.dependence[inst.rs2])
                            self.A[i] = Bits(32)(0)
                            self.Dest[i] = inst_id
                        with Condition(inst.Type == Bits(32)(2)): #Type I
                            self.Busy[i] = Bits(1)(1)
                            self.Op_id[i] = inst.id
                            self.Vj[i] = (rf.dependence[inst.rs1] == Bits(32)(0)).select(rf.val[inst.rs1], Bits(32)(0))
                            self.Vk[i] = Bits(32)(0)
                            self.Qj[i] = (rf.dependence[inst.rs1] == Bits(32)(0)).select(Bits(32)(0), rf.dependence[inst.rs1])
                            self.Qk[i] = Bits(32)(0)
                            self.A[i] = inst.imm
                            self.Dest[i] = inst_id
                        with Condition(inst.Type == Bits(32)(4)): # Type B
                            self.Busy[i] = Bits(1)(1)
                            self.Op_id[i] = inst.id
                            self.Vj[i] = (rf.dependence[inst.rs1] == Bits(32)(0)).select(rf.val[inst.rs1], Bits(32)(0))
                            self.Vk[i] = (rf.dependence[inst.rs2] == Bits(32)(0)).select(rf.val[inst.rs2], Bits(32)(0))
                            self.Qj[i] = (rf.dependence[inst.rs1] == Bits(32)(0)).select(Bits(32)(0), rf.dependence[inst.rs1])
                            self.Qk[i] = (rf.dependence[inst.rs2] == Bits(32)(0)).select(Bits(32)(0), rf.dependence[inst.rs2])
                            self.A[i] = inst.imm
                            self.Dest[i] = inst_id
                    once_tag = once_tag & self.Busy[i]

        self.log()