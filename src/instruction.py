from dis import Instruction

from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

Id_to_Instruction_Name = {
    Bits(32)(1): "add",
    Bits(32)(2): "sub",
    Bits(32)(3): "and",
    Bits(32)(4): "or",
    Bits(32)(5): "xor",
    Bits(32)(6): "sll",
    Bits(32)(7): "srl",
    Bits(32)(8): "sra",
    Bits(32)(9): "slt",
    Bits(32)(10): "sltu",

    Bits(32)(11): "addi",
    Bits(32)(12): "andi",
    Bits(32)(13): "ori",
    Bits(32)(14): "xori",
    Bits(32)(15): "slli",
    Bits(32)(16): "srli",
    Bits(32)(17): "srai",
    Bits(32)(18): "slti",
    Bits(32)(19): "sltiu",

    Bits(32)(20): "lb",
    Bits(32)(21): "lbu",
    Bits(32)(22): "lh",
    Bits(32)(23): "lhu",
    Bits(32)(24): "lw",

    Bits(32)(25): "sb",
    Bits(32)(26): "sh",
    Bits(32)(27): "sw",

    Bits(32)(28): "beq",
    Bits(32)(29): "bge",
    Bits(32)(30): "bgeu",
    Bits(32)(31): "blt",
    Bits(32)(32): "bltu",
    Bits(32)(33): "bne",

    Bits(32)(34): "jal",

    Bits(32)(35): "jalr",

    Bits(32)(36): "auipc",
    Bits(32)(37): "lui",
}

Number_to_Register_Name = [
    "zero",
    "ra",
    "sp",
    "gp",
    "tp",
    "t0",
    "t1",
    "t2",
    "s0",
    "s1",
    "a0",
    "a1",
    "a2",
    "a3",
    "a4",
    "a5",
    "a6",
    "a7",
    "s2",
    "s3",
    "s4",
    "s5",
    "s6",
    "s7",
    "s8",
    "s9",
    "s10",
    "s11",
    "t3",
    "t4",
    "t5",
    "t6"
]

def get_int_val(v: Bits, hb):#[0,hb]
    res = v.bitcast(Int(32))
    res = (((Bits(32)(1) << Bits(32)(hb)) & v) != Bits(32)(0)).select(v.bitcast(Int(32)) - Int(32)(1 << hb) - Int(32)(1 << hb), res)
    return res

class Inst:
    rd: Bits
    rs1: Bits
    rs2: Bits
    imm: Bits

    Type: Bits
    id: Bits

    def __init__(self, rd, rs1, rs2, imm, Type, id):
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
        self.Type = Type
        self.id = id

    def if_change(self, if_cond, change_value):
        self.rd = if_cond.select(change_value.rd, self.rd)
        self.rs1 = if_cond.select(change_value.rs1, self.rs1)
        self.rs2 = if_cond.select(change_value.rs2, self.rs2)
        self.imm = if_cond.select(change_value.imm, self.imm)
        self.Type = if_cond.select(change_value.Type, self.Type)
        self.id = if_cond.select(change_value.id, self.id)
        return self

    def show(self):
        with Condition(self.id == Bits(32)(0)):
            log("Invalid Inst")
        for index, name in Id_to_Instruction_Name.items():
            with Condition(index == self.id):
                # log(f"found id = {{}}, inst = {name}", index)
                with Condition(self.Type == Bits(32)(1)):
                    log(f"inst = {name}, rd = ~{{}}~, rs1 = ~{{}}~, rs2 = ~{{}}~ --- [Type R]", self.rd, self.rs1, self.rs2)
                with Condition(self.Type == Bits(32)(2)):
                    imm = self.imm.bitcast(Int(32))
                    imm = (self.id == Bits(32)(18)).select(get_int_val(self.imm, 11), imm) # slti
                    imm = (self.id == Bits(32)(20)).select(get_int_val(self.imm, 11), imm) # lb
                    imm = (self.id == Bits(32)(22)).select(get_int_val(self.imm, 11), imm)  # lh
                    imm = (self.id == Bits(32)(24)).select(get_int_val(self.imm, 11), imm)  # lw
                    imm = (self.id == Bits(32)(35)).select(get_int_val(self.imm, 11), imm)  # jalr
                    log(f"inst = {name}, rd = ~{{}}~, rs1 = ~{{}}~, imm = {{}} --- [Type I]", self.rd, self.rs1, imm)
                with Condition(self.Type == Bits(32)(3)):
                    imm = get_int_val(self.imm, 11) # sb & sh & sw
                    log(f"inst = {name}, rs2 = ~{{}}~, imm = {{}}, ( rs1 = ~{{}}~ ) --- [Type S]", self.rs2, imm, self.rs1)
                with Condition(self.Type == Bits(32)(4)):
                    imm = self.imm.bitcast(Int(32))
                    imm = (self.id == Bits(32)(28)).select(get_int_val(self.imm, 12), imm)  # beq
                    imm = (self.id == Bits(32)(29)).select(get_int_val(self.imm, 12), imm)  # bge
                    imm = (self.id == Bits(32)(31)).select(get_int_val(self.imm, 12), imm)  # blt
                    imm = (self.id == Bits(32)(33)).select(get_int_val(self.imm, 12), imm)  # bne
                    log(f"inst = {name}, rs1 = ~{{}}~, rs2 = ~{{}}~, offset(store as imm) = {{}} --- [Type B]", self.rs1, self.rs2, imm)
                with Condition(self.Type == Bits(32)(5)):
                    imm = get_int_val(self.imm, 20)  # jal
                    log(f"inst = {name}, rd = ~{{}}~, offset(store as imm) = {{}} --- [Type J]", self.rd, imm)
                with Condition(self.Type == Bits(32)(6)):
                    log(f"inst = {name}, rd = ~{{}}~, immu = {{}} --- [Type U]", self.rd, self.imm)