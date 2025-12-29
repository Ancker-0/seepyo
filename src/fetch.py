from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

ADDR_WIDTH = 12
INST_WIDTH = 32

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
        log("we: {} | re: {} | addr: {} | dout: {}", we, re, address_wire, sram.dout[0])
        (val&self)[0] <= sram.dout[0]
        log('Got inst {}', val[0])