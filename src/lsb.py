from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

from register import Register
from rob import ROB
from src.const import ADDR_WIDTH, INST_WIDTH, LSB_SIZE
from src.instruction import Inst
from toolbox import RegArrays

def isLoad(id):
    return (Bits(32)(19) < id) & (id < Bits(32)(25))

def isStore(id):
    return (Bits(32)(24) < id) & (id < Bits(32)(28))

class LSB(Module):
    def __init__(self):
        super().__init__(ports = {
            "p_opid": Port(Bits(32)),
            "p_rs1": Port(Bits(32)),
            "p_rs2": Port(Bits(32)),
            "p_imm": Port(Bits(32)),
            "p_fetchid": Port(Bits(32)),
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
        self.fetch_id = RegArrays(Bits(32), LSB_SIZE, self)
        self.imm = RegArrays(Bits(32), LSB_SIZE, self)
        self.done = RegArrays(Bits(1), LSB_SIZE, self)

        self.sram = SRAM(32, 2 ** ADDR_WIDTH, init_file=None)

    def clean(self, Id):
        self.opid[Id] = Bits(32)(0)
        self.Vj[Id] = Bits(32)(0)
        self.Vk[Id] = Bits(32)(0)
        self.Qj[Id] = Bits(32)(0)
        self.Qk[Id] = Bits(32)(0)
        self.fetch_id[Id] = Bits(32)(0)
        self.imm[Id] = Bits(32)(0)
        self.done[Id] = Bits(1)(0)

    def log(self):
        log("------- LSB log start -------")
        for i in range(self.size):
            log("Op = ${}$, Vj = {}, Vk = {}, Qj = {}, Qk = {}, imm = {}, rd_robid = {}, Done = {}",
                self.opid[i], self.Vj[i], self.Vk[i], self.Qj[i], self.Qk[i], self.imm[i], self.fetch_id[i], self.done[i])
        log("------- LSB log end -------")
    
    def avail(self):
        ret = Bits(1)(0)
        for i in range(self.size):
            ret = ret | (self.opid[i] == Bits(32)(0))
        return ret

    def no_dep(self, fetchid):
        ret = Bits(1)(1)
        for i in range(self.size):
            ret = ret & (~isStore(self.opid[i]) | (fetchid < self.fetch_id[i]))
        return ret

    def entry_by_fetchid(self, idx):
        ret = Bits(1)(0)
        for i in range(self.size):
            ret = ret & (self.fetch_id[i] == idx)
        return ret

    @module.combinational
    def build(self, rf: Register, rob: ROB):
        we = RegArrays(Bits(1), 1, self)
        re = RegArrays(Bits(1), 1, self)
        address_wire = RegArrays(Bits(32), 1, self)
        wdata = RegArrays(Bits(32), 1, self)
        self.sram.build(we[0], re[0], address_wire[0], wdata[0])
        read_entry = RegArrays(Bits(32), 1, self, [self.size])
        waiting = RegArrays(Bits(1), 1, self)

        flush = self.flush_tag.valid()
        with Condition(flush):
            for i in range(self.size):
                self.clean(i)
            for port in self.ports:
                with Condition(port.valid()):
                    port.pop()
        with Condition(~flush):
            with Condition(self.p_opid.valid() & self.avail()):
                opid = self.p_opid.pop()
                rs1 = self.p_rs1.pop()
                rs2 = self.p_rs2.pop()
                imm = self.p_imm.pop()
                fetch_id = self.p_fetchid.pop()
                once_tag = Bits(1)(1)
                for i in range(self.size):
                    avail = self.opid[i] == Bits(32)(0)
                    with Condition(once_tag & avail):
                        with Condition(opid == Bits(32)(24)):  # lw
                            self.opid[i] = opid
                            self.Vj[i] = (rf.dependence[rs1] == Bits(32)(0)).select(rf.val[rs1], Bits(32)(0))
                            self.Vk[i] = Bits(32)(0)
                            self.Qj[i] = (rf.dependence[rs1] == Bits(32)(0)).select(Bits(32)(0), rf.dependence[rs1])
                            self.Qk[i] = Bits(32)(0)
                            self.fetch_id[i] = fetch_id
                            self.imm[i] = imm
                            self.done[i] = Bits(1)(0)
                        with Condition(opid == Bits(32)(27)):  # sw
                            self.opid[i] = opid
                            self.Vj[i] = (rf.dependence[rs1] == Bits(32)(0)).select(rf.val[rs1], Bits(32)(0))
                            self.Vk[i] = (rf.dependence[rs2] == Bits(32)(0)).select(rf.val[rs2], Bits(32)(0))
                            Qj = (rf.dependence[rs1] == Bits(32)(0)).select(Bits(32)(0), rf.dependence[rs1])
                            Qk = (rf.dependence[rs2] == Bits(32)(0)).select(Bits(32)(0), rf.dependence[rs2])
                            self.Qj[i] = Qj
                            self.Qk[i] = Qk
                            self.fetch_id[i] = fetch_id
                            self.imm[i] = imm
                            self.done[i] = Bits(1)(0)
                            # with Condition((Qj == Bits(32)(0)) & (Qk == Bits(32)(0))):
                            #     rob_entry = rob.entry_by_fetch_id(fetch_id)
                            #     log("Got two Zs! cleaning {}", rob_entry)
                            #     rob.busy[rob_entry] = Bits(1)(0)
                    once_tag = once_tag & ~avail


            peek_robid = self.p_robid.valid().select(self.p_robid.peek(), Bits(32)(0))
            # done things for ROB
            with Condition(self.p_robid.valid()):
                rob_id = self.p_robid.pop()
                rob_value = self.p_robval.pop()
                once_tag = Bits(1)(1)
                for i in range(self.size):
                    with Condition(self.opid[i] != Bits(32)(0)):
                        with Condition(self.Qj[i] == rob_id):
                            self.Vj[i] = rob_value
                            self.Qj[i] = Bits(32)(0)
                        with Condition(self.Qk[i] == rob_id):
                            self.Vk[i] = rob_value
                            self.Qk[i] = Bits(32)(0)
                        Qj = (self.Qj[i] == Bits(32)(0)) | (self.Qj[i] == rob_id)
                        Qk = (self.Qk[i] == Bits(32)(0)) | (self.Qk[i] == rob_id)
                        #some = (self.Qj[i] == rob_id) | (self.Qk[i] == rob_id)
                        #with Condition(Qj & Qk & some):
                        #    rob_entry = rob.entry_by_fetch_id(self.fetch_id[i])
                        #    log("Got ZZs! cleaning {}", rob_entry)
                        #    rob.busy[rob_entry] = Bits(1)(0)
                    with Condition((self.fetch_id[i] == rob_id) & isStore(self.opid[i]) & once_tag):
                        we[0] = Bits(1)(1)
                        re[0] = Bits(1)(0)
                        address_wire[0] = (self.Vj[i] + self.imm[i]) >> Bits(32)(2)
                        wdata[0] = self.Vk[i]
                        self.clean(i)
                        log("issue writing addr = {}, data = {}", (self.Vj[i] + self.imm[i]) >> Bits(32)(2), self.Vk[i])
                    once_tag = once_tag & ~((self.fetch_id[i] == rob_id) & isStore(self.opid[i]) & once_tag)

            # ask sram
            with Condition(~waiting[0] & (read_entry[0] == Bits(32)(self.size))):
                once_tag = Bits(1)(1)
                for i in range(self.size):
                    once_tag = once_tag & ~((self.fetch_id[i] == peek_robid) & isStore(self.opid[i]) & once_tag)
                once_tag = once_tag | ~self.p_robid.valid()
                for i in range(self.size):
                    loadCan = (self.opid[i] == Bits(32)(24)) & (self.Qj[i] == Bits(32)(0)) & self.no_dep(self.fetch_id[i])
                    with Condition(once_tag & loadCan):  # lb
                        we[0] = Bits(1)(0)
                        re[0] = Bits(1)(1)
                        address_wire[0] = (self.Vj[i] + self.imm[i]) >> Bits(32)(2)
                        read_entry[0] = Bits(32)(i)
                        waiting[0] = Bits(1)(1)
                        log("issue reading addr = {}", (self.Vj[i] + self.imm[i]) >> Bits(32)(2))
                    once_tag = once_tag & (~loadCan)

            with Condition(read_entry[0] != Bits(32)(self.size)):
                with Condition(waiting[0]):
                    log("waiting for sram")
                    waiting[0] = Bits(1)(0)
                with Condition(~waiting[0]):
                    read_entry[0] <= Bits(32)(self.size)
                    id = read_entry[0]
                    log("received dram data entry_id = {}", id)
                    self.clean(id)
                    rob_entry = rob.entry_by_fetch_id(self.fetch_id[id])
                    rob.value[rob_entry] = self.sram.dout[0]
                    rob.busy[rob_entry] = Bits(1)(0)

        self.log()