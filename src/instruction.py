from dis import Instruction

from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator
from const import INST_WIDTH

Id_to_Instruction_Name = {
    1: "add",
    2: "sub",
    3: "and",
    4: "or",
    5: "xor",
    6: "sll",
    7: "srl",
    8: "sra",
    9: "slt",
    10: "sltu",

    11: "addi",
    12: "andi",
    13: "ori",
    14: "xori",
    15: "slli",
    16: "srli",
    17: "srai",
    18: "slti",
    19: "sltiu",

    20: "lb",
    21: "lbu",
    22: "lh",
    23: "lhu",
    24: "lw",

    25: "sb",
    26: "sh",
    27: "sw",

    28: "beq",
    29: "bge",
    30: "bgeu",
    31: "blt",
    32: "bltu",
    33: "bne",

    34: "jal",

    35: "jalr",

    36: "auipc",
    37: "lui",
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

Id_Type_Map = {
    Bits(32)(0): Bits(32)(0),

    Bits(32)(1): Bits(32)(1),
    Bits(32)(2): Bits(32)(1),
    Bits(32)(3): Bits(32)(1),
    Bits(32)(4): Bits(32)(1),
    Bits(32)(5): Bits(32)(1),
    Bits(32)(6): Bits(32)(1),
    Bits(32)(7): Bits(32)(1),
    Bits(32)(8): Bits(32)(1),
    Bits(32)(9): Bits(32)(1),
    Bits(32)(10): Bits(32)(1),

    Bits(32)(11): Bits(32)(2),
    Bits(32)(12): Bits(32)(2),
    Bits(32)(13): Bits(32)(2),
    Bits(32)(14): Bits(32)(2),
    Bits(32)(15): Bits(32)(2),
    Bits(32)(16): Bits(32)(2),
    Bits(32)(17): Bits(32)(2),
    Bits(32)(18): Bits(32)(2),
    Bits(32)(19): Bits(32)(2),

    Bits(32)(20): Bits(32)(2),
    Bits(32)(21): Bits(32)(2),
    Bits(32)(22): Bits(32)(2),
    Bits(32)(23): Bits(32)(2),
    Bits(32)(24): Bits(32)(2),

    Bits(32)(25): Bits(32)(3),
    Bits(32)(26): Bits(32)(3),
    Bits(32)(27): Bits(32)(3),

    Bits(32)(28): Bits(32)(4),
    Bits(32)(29): Bits(32)(4),
    Bits(32)(30): Bits(32)(4),
    Bits(32)(31): Bits(32)(4),
    Bits(32)(32): Bits(32)(4),
    Bits(32)(33): Bits(32)(4),

    Bits(32)(34): Bits(32)(5),

    Bits(32)(35): Bits(32)(2),

    Bits(32)(36): Bits(32)(6),
    Bits(32)(37): Bits(32)(6),
}

def inst_id_to_type(id):
    res = Bits(32)(0)
    for Id, Type in Id_Type_Map.items():
        res = (id == Id).select(Type, res)
    return res

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
            with Condition(Bits(32)(index) == self.id):
                # log(f"found id = {{}}, inst = {name}", index)
                with Condition(self.Type == Bits(32)(1)):
                    log(f"inst = {name}, rd = ~{{}}~, rs1 = ~{{}}~, rs2 = ~{{}}~ --- [Type R]", self.rd, self.rs1, self.rs2)
                with Condition(self.Type == Bits(32)(2)):
                    imm = self.imm
                    #imm = self.imm.bitcast(Int(32))
                    #imm = (self.id == Bits(32)(18)).select(get_int_val(self.imm, 11), imm) # slti
                    #imm = (self.id == Bits(32)(20)).select(get_int_val(self.imm, 11), imm) # lb
                    #imm = (self.id == Bits(32)(22)).select(get_int_val(self.imm, 11), imm)  # lh
                    #imm = (self.id == Bits(32)(24)).select(get_int_val(self.imm, 11), imm)  # lw
                    #imm = (self.id == Bits(32)(35)).select(get_int_val(self.imm, 11), imm)  # jalr
                    log(f"inst = {name}, rd = ~{{}}~, rs1 = ~{{}}~, imm = {{:X}} --- [Type I]", self.rd, self.rs1, imm)
                with Condition(self.Type == Bits(32)(3)):
                    imm = self.imm
                    #imm = get_int_val(self.imm, 11) # sb & sh & sw
                    log(f"inst = {name}, rs2 = ~{{}}~, imm = {{:X}}, ( rs1 = ~{{}}~ ) --- [Type S]", self.rs2, imm, self.rs1)
                with Condition(self.Type == Bits(32)(4)):
                    imm = self.imm
                    #imm = self.imm.bitcast(Int(32))
                    #imm = (self.id == Bits(32)(28)).select(get_int_val(self.imm, 12), imm)  # beq
                    #imm = (self.id == Bits(32)(29)).select(get_int_val(self.imm, 12), imm)  # bge
                    #imm = (self.id == Bits(32)(31)).select(get_int_val(self.imm, 12), imm)  # blt
                    #imm = (self.id == Bits(32)(33)).select(get_int_val(self.imm, 12), imm)  # bne
                    log(f"inst = {name}, rs1 = ~{{}}~, rs2 = ~{{}}~, offset(store as imm) = {{:X}} --- [Type B]", self.rs1, self.rs2, imm)
                with Condition(self.Type == Bits(32)(5)):
                    imm = self.imm
                    #imm = get_int_val(self.imm, 20)  # jal
                    log(f"inst = {name}, rd = ~{{}}~, offset(store as imm) = {{:X}} --- [Type J]", self.rd, imm)
                with Condition(self.Type == Bits(32)(6)):
                    log(f"inst = {name}, rd = ~{{}}~, immu = {{:X}} --- [Type U]", self.rd, self.imm)