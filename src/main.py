import os
import sys as Sys

from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

from fetch import Fetcher
from src.instruction import Instruction, Number_to_Register_Name, Id_to_Instruction_Name
from const import INST_WIDTH, ADDR_WIDTH
from rs import RS
from register import Register
from rob import ROB
from alu import ALU

class Test_Part(Module):
    def __init__(self):
        super().__init__({})

    @module.combinational
    def build(self, rf, rs):
        rf.update(Bits(32)(6), Bits(32)(113), Bits(32)(0))
        # rf.update(Bits(32)(2), Bits(32)(0), Bits(32)(2))  # This creates incorrect dependence!
        # for i in range(32):
        #     rf.update(Bits(32)(i), Bits(32)(421 & (((i & 1) << 10) - 1)), Bits(32)(2 & ((((i & 1) ^ 1) << 10) - 1)))

class Driver(Module):
    def __init__(self):
        super().__init__({})

    @module.combinational
    def build(self, fetcher: Fetcher):
        fetcher.async_called()

def build():
    sys = SysBuilder('seepyo')
    with sys:
        rob_reset, rob_PC = RegArray(Bits(1), 1), RegArray(Bits(32), 1)
        fetcher = Fetcher(rob_reset, rob_PC)
        init_file = Sys.argv[1] if len(Sys.argv) >= 2 else 'term_test.data'
        sram = SRAM(INST_WIDTH, 2 ** ADDR_WIDTH, init_file)

        driver = Driver()
        # test_part = Test_Part()
        rf = Register()
        rs = RS()
        robL, robR = RegArray(Bits(32), 1, [0]), RegArray(Bits(32), 1, [0])
        rob = ROB(robL, robR, rob_reset, rob_PC)
        alu = ALU()

        we, re, address_wire, write_wire = fetcher.build(sram, rs, rob, test_part=None, rob_R=robR)
        sram.build(we, re, address_wire, write_wire)


        driver.build(fetcher)
        rf.build()  # Initialize RF dependence to 0
        rs.build(rf, alu)  # RS 需要引用 ALU 来发射指令
        rob.build(rf, rs)
        alu.build(rob, rs)
        # test_part.build(rf, rs)
    return sys

def main():
    sys = build()
    resource_path = os.path.join(os.path.dirname(__file__), "..", "data")
    sim, verilog = elaborate(sys, verbose=True, simulator=True, verilog=False, resource_base=resource_path, sim_threshold=600)
    output = run_simulator(sim)

    for [Id, reg_name] in enumerate(Number_to_Register_Name):
        # print(id, reg_name)
        output = output.replace(f'~{Id}~', reg_name)
    for [Id, inst_name] in Id_to_Instruction_Name.items():
        output = output.replace(f'${Id}$', inst_name)

    print(output)
main()
