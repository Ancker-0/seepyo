import os

from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

from fetch import Fetcher
from src.instruction import Instruction, Number_to_Register_Name


class Driver(Module):
    def __init__(self):
        super().__init__({})

    @module.combinational
    def build(self, fetcher: Fetcher):
        fetcher.async_called()

def build():
    sys = SysBuilder('seepyo')
    with sys:
        fetcher = Fetcher()
        driver = Driver()

        init_file = 'test.data'
        fetcher.build(init_file)
        driver.build(fetcher)
    return sys

def main():
    sys = build()
    resource_path = os.path.join(os.path.dirname(__file__), "..", "data")
    sim, verilog = elaborate(sys, verbose=True, simulator=True, verilog=True, resource_base=resource_path)
    output = run_simulator(sim)

    for [id, reg_name] in enumerate(Number_to_Register_Name):
        # print(id, reg_name)
        output = output.replace(f'~{id}~', reg_name)

    print(output)
main()