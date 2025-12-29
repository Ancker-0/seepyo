import os

from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

from fetch import Fetcher

class Driver(Module):
    def __init__(self):
        super().__init__({})

    @module.combinational
    def build(self):
        pass

def build():
    sys = SysBuilder('seepyo')
    with sys:
        fetcher = Fetcher()
        driver = Driver()

        init_file = 'test.data'
        fetcher.build(init_file)
        driver.build()
    return sys

def main():
    sys = build()
    sim, verilog = elaborate(sys, verbose=True, simulator=True, verilog=True, resource_base='./data/')
    output = run_simulator(sim)
    print(output)
main()