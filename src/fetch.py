from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

ADDR_WIDTH = 12

class Fetcher(Module):
    def __init__(self):
        super().__init__({})

    @module.combinational
    def build(self, init_file: str):
        sram = SRAM(32, 2**ADDR_WIDTH, init_file)