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
        sram = SRAM(INST_WIDTH, 2**ADDR_WIDTH, init_file)
        re = Bits(1)(0)
        we = Bits(1)(0)
        address_wire = Bits(ADDR_WIDTH)(0)
        write_wire = Bits(INST_WIDTH)(0)
        sram.build(we, re, address_wire, write_wire)
        sram.dout
        val = sram.dout[0]
        log('{}', val)