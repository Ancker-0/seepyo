from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

from instruction import *

ADDR_WIDTH = 12
INST_WIDTH = 32

def get_number_range(v: Bits, l: int, r: int):
    # get [l,r] of the Bits, 0-index
    sz = r - l + 1
    log("v: {}, sz: {}", v, Bits(INST_WIDTH)(sz))
    tmp = v >> Bits(INST_WIDTH)(l)
    if sz < 32 :
        tmp &= (Bits(INST_WIDTH)(1) << Bits(INST_WIDTH)(sz)) - Bits(INST_WIDTH)(1)
    return tmp

class Fetcher(Module):
    def __init__(self):
        super().__init__({})

    @module.combinational
    def build(self, init_file: str):
        we = Bits(1)(0)
        re = ~we
        # re = Bits(1)(1)
        address_wire = Bits(ADDR_WIDTH)(1)
        write_wire = Bits(INST_WIDTH)(0)

        sram = SRAM(INST_WIDTH, 2**ADDR_WIDTH, init_file)
        sram.build(we, re, address_wire, write_wire)
        val = RegArray(Bits(32), 1)
        log("we: {} | re: {} | addr: {} | dout: {} | or {}", we, re, address_wire, sram.dout[0], get_number_range(sram.dout[0], 0, 0))
        (val&self)[0] <= sram.dout[0]
        log('Got inst {}', val[0])

        tmp: Instruction = Inst(Bits(32)(1), Bits(32)(1), Bits(32)(1), Bits(32)(1), Bits(32)(1), Bits(32)(1))
        tmp.show()
        tmp.Type = Bits(32)(2)
        tmp.show()
        tmp.Type = Bits(32)(3)
        tmp.show()
        tmp.Type = Bits(32)(4)
        tmp.show()
        tmp.Type = Bits(32)(5)
        tmp.show()
        tmp.Type = Bits(32)(6)
        tmp.show()
        tmp.Type = Bits(32)(7)
        tmp.show()