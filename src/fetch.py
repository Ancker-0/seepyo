from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

from instruction import *
from const import INST_WIDTH, ADDR_WIDTH


def get_number_range(v: Bits, l: int, r: int):
    # get [l,r] of the Bits, 0-index
    sz = r - l + 1
    tmp = (v >> Bits(INST_WIDTH)(l))
    if sz < 32:
        tmp &= (Bits(INST_WIDTH)(1) << Bits(INST_WIDTH)(sz)) - Bits(INST_WIDTH)(1)
    return tmp

def get_number_range_multiple(v: Bits, *args):# can't use [0,0]
    sz = 0
    tmp = Bits(INST_WIDTH)(0)
    for cov in args:
        if cov[1] > 0:
            tmp += (get_number_range(v, cov[0], cov[1]) << Bits(INST_WIDTH)(sz))
            sz += cov[1] - cov[0] + 1
        else:
            sz += cov[0]
    return tmp

def decode_typeR(v: Bits):
    funct7 = get_number_range(v, 25, 31)
    rs2 = get_number_range(v, 20, 24)
    rs1 = get_number_range(v, 15, 19)
    funct3 = get_number_range(v, 12, 14)
    rd = get_number_range(v, 7, 11)

    Id = Bits(INST_WIDTH)(0)

    # add
    Id = ((funct7 == Bits(INST_WIDTH)(0b0000000)) & (funct3 == Bits(INST_WIDTH)(0b000))).select(Bits(INST_WIDTH)(1), Id)
    # sub
    Id = ((funct7 == Bits(INST_WIDTH)(0b0100000)) & (funct3 == Bits(INST_WIDTH)(0b000))).select(Bits(INST_WIDTH)(2), Id)
    # and
    Id = ((funct7 == Bits(INST_WIDTH)(0b0000000)) & (funct3 == Bits(INST_WIDTH)(0b111))).select(Bits(INST_WIDTH)(3), Id)
    # or
    Id = ((funct7 == Bits(INST_WIDTH)(0b0000000)) & (funct3 == Bits(INST_WIDTH)(0b110))).select(Bits(INST_WIDTH)(4), Id)
    # xor
    Id = ((funct7 == Bits(INST_WIDTH)(0b0000000)) & (funct3 == Bits(INST_WIDTH)(0b100))).select(Bits(INST_WIDTH)(5), Id)
    # sll
    Id = ((funct7 == Bits(INST_WIDTH)(0b0000000)) & (funct3 == Bits(INST_WIDTH)(0b001))).select(Bits(INST_WIDTH)(6), Id)
    # srl
    Id = ((funct7 == Bits(INST_WIDTH)(0b0000000)) & (funct3 == Bits(INST_WIDTH)(0b101))).select(Bits(INST_WIDTH)(7), Id)
    # sra
    Id = ((funct7 == Bits(INST_WIDTH)(0b1000000)) & (funct3 == Bits(INST_WIDTH)(0b101))).select(Bits(INST_WIDTH)(8), Id)
    # slt
    Id = ((funct7 == Bits(INST_WIDTH)(0b0000000)) & (funct3 == Bits(INST_WIDTH)(0b010))).select(Bits(INST_WIDTH)(9), Id)
    # sltu
    Id = ((funct7 == Bits(INST_WIDTH)(0b0000000)) & (funct3 == Bits(INST_WIDTH)(0b011))).select(Bits(INST_WIDTH)(10),
                                                                                                Id)
    imm = Bits(INST_WIDTH)(0)
    Type = Bits(INST_WIDTH)(1)

    return Inst(rd, rs1, rs2, imm, Type, Id)

def decode_typeI(v: Bits):
    opcode = get_number_range(v, 0, 6)
    rd = get_number_range(v, 7, 11)
    funct3 = get_number_range(v, 12, 14)
    rs1 = get_number_range(v, 15, 19)
    imm11_0 = get_number_range(v, 20, 31)
    imm4_0 = get_number_range(v, 20, 24)

    # 对于移位立即数指令，需要检查funct7字段
    funct7 = get_number_range(v, 25, 31)

    # I-type指令没有rs2，设为0
    rs2 = Bits(INST_WIDTH)(0)

    Id = Bits(INST_WIDTH)(0)

    # addi
    Id = ((opcode == Bits(INST_WIDTH)(0b0010011)) & (funct3 == Bits(INST_WIDTH)(0b000))).select(Bits(INST_WIDTH)(11), Id)
    # andi
    Id = ((opcode == Bits(INST_WIDTH)(0b0010011)) & (funct3 == Bits(INST_WIDTH)(0b111))).select(Bits(INST_WIDTH)(12), Id)
    # ori
    Id = ((opcode == Bits(INST_WIDTH)(0b0010011)) & (funct3 == Bits(INST_WIDTH)(0b110))).select(Bits(INST_WIDTH)(13), Id)
    # xori
    Id = ((opcode == Bits(INST_WIDTH)(0b0010011)) & (funct3 == Bits(INST_WIDTH)(0b100))).select(Bits(INST_WIDTH)(14), Id)
    # slli
    Id = ((opcode == Bits(INST_WIDTH)(0b0010011)) & (funct3 == Bits(INST_WIDTH)(0b001)) & (
                funct7 == Bits(INST_WIDTH)(0b0000000))).select(Bits(INST_WIDTH)(15), Id)
    # srli
    Id = ((opcode == Bits(INST_WIDTH)(0b0010011)) & (funct3 == Bits(INST_WIDTH)(0b101)) & (
                funct7 == Bits(INST_WIDTH)(0b0000000))).select(Bits(INST_WIDTH)(16), Id)
    # srai
    Id = ((opcode == Bits(INST_WIDTH)(0b0010011)) & (funct3 == Bits(INST_WIDTH)(0b101)) & (
                funct7 == Bits(INST_WIDTH)(0b0100000))).select(Bits(INST_WIDTH)(17), Id)
    # slti
    Id = ((opcode == Bits(INST_WIDTH)(0b0010011)) & (funct3 == Bits(INST_WIDTH)(0b010))).select(Bits(INST_WIDTH)(18), Id)
    # sltiu
    Id = ((opcode == Bits(INST_WIDTH)(0b0010011)) & (funct3 == Bits(INST_WIDTH)(0b011))).select(Bits(INST_WIDTH)(19), Id)
    # lb
    Id = ((opcode == Bits(INST_WIDTH)(0b0000011)) & (funct3 == Bits(INST_WIDTH)(0b000))).select(Bits(INST_WIDTH)(20), Id)
    # lbu
    Id = ((opcode == Bits(INST_WIDTH)(0b0000011)) & (funct3 == Bits(INST_WIDTH)(0b100))).select(Bits(INST_WIDTH)(21), Id)
    # lh
    Id = ((opcode == Bits(INST_WIDTH)(0b0000011)) & (funct3 == Bits(INST_WIDTH)(0b001))).select(Bits(INST_WIDTH)(22), Id)
    # lhu
    Id = ((opcode == Bits(INST_WIDTH)(0b0000011)) & (funct3 == Bits(INST_WIDTH)(0b101))).select(Bits(INST_WIDTH)(23), Id)
    # lw
    Id = ((opcode == Bits(INST_WIDTH)(0b0000011)) & (funct3 == Bits(INST_WIDTH)(0b010))).select(Bits(INST_WIDTH)(24), Id)
    # jalr
    Id = (opcode == Bits(INST_WIDTH)(0b1100111)).select(Bits(INST_WIDTH)(35), Id)

    Type = Bits(INST_WIDTH)(2)

    imm = ((Id >= Bits(INST_WIDTH)(15)) & (Id <= Bits(INST_WIDTH)(17))).select(imm4_0, imm11_0)

    return Inst(rd, rs1, rs2, imm, Type, Id)

def decode_typeS(v: Bits):
    rs1 = get_number_range(v, 15, 19)
    rs2 = get_number_range(v, 20, 24)
    funct3 = get_number_range(v, 12, 14)
    rd = Bits(INST_WIDTH)(0)
    imm = get_number_range_multiple(v, [7, 11], [25, 31])

    Id = Bits(INST_WIDTH)(0)

    # sb
    Id = (funct3 == Bits(INST_WIDTH)(0b000)).select(Bits(INST_WIDTH)(25), Id)
    # sh
    Id = (funct3 == Bits(INST_WIDTH)(0b001)).select(Bits(INST_WIDTH)(26), Id)
    # sw
    Id = (funct3 == Bits(INST_WIDTH)(0b010)).select(Bits(INST_WIDTH)(27), Id)

    Type = Bits(INST_WIDTH)(3)

    return Inst(rd, rs1, rs2, imm, Type, Id)

def decode_typeB(v: Bits):
    rs1 = get_number_range(v, 15, 19)
    rs2 = get_number_range(v, 20, 24)
    funct3 = get_number_range(v, 12, 14)
    imm = get_number_range_multiple(v, [1, 0], [8, 11], [25, 30], [7, 7], [31, 31])

    rd = Bits(INST_WIDTH)(0)
    Id = Bits(INST_WIDTH)(0)

    #beq
    Id = (funct3 == Bits(INST_WIDTH)(0b000)).select(Bits(INST_WIDTH)(28), Id)
    #bge
    Id = (funct3 == Bits(INST_WIDTH)(0b101)).select(Bits(INST_WIDTH)(29), Id)
    #bgeu
    Id = (funct3 == Bits(INST_WIDTH)(0b111)).select(Bits(INST_WIDTH)(30), Id)
    # blt
    Id = (funct3 == Bits(INST_WIDTH)(0b100)).select(Bits(INST_WIDTH)(31), Id)
    # bltu
    Id = (funct3 == Bits(INST_WIDTH)(0b110)).select(Bits(INST_WIDTH)(32), Id)
    # bne
    Id = (funct3 == Bits(INST_WIDTH)(0b001)).select(Bits(INST_WIDTH)(33), Id)

    Type = Bits(INST_WIDTH)(4)

    return Inst(rd, rs1, rs2, imm, Type, Id)

def decode_typeJ(v: Bits):
    rd = get_number_range(v, 7, 11)
    imm = get_number_range_multiple(v, [1, 0], [21, 30], [20, 20], [12, 19], [31, 31])

    rs1 = Bits(INST_WIDTH)(0)
    rs2 = Bits(INST_WIDTH)(0)

    #jal
    Id = Bits(INST_WIDTH)(34)

    Type = Bits(INST_WIDTH)(5)

    return Inst(rd, rs1, rs2, imm, Type, Id)

def decode_typeU(v: Bits):
    Opcode = get_number_range(v, 0, 6)
    rd = get_number_range(v, 7, 11)
    imm = get_number_range_multiple(v, [12, 0], [12, 31])

    rs1 = Bits(INST_WIDTH)(0)
    rs2 = Bits(INST_WIDTH)(0)
    Id = Bits(INST_WIDTH)(0)

    # auipc
    Id = (Opcode == Bits(INST_WIDTH)(0b0010111)).select(Bits(INST_WIDTH)(36), Id)
    # lui
    Id = (Opcode == Bits(INST_WIDTH)(0b0110111)).select(Bits(INST_WIDTH)(37), Id)

    Type = Bits(INST_WIDTH)(6)

    return Inst(rd, rs1, rs2, imm, Type, Id)

def decode_inst(v: Bits):
    Opcode = get_number_range(v, 0, 6)
    res = Inst(Bits(32)(0), Bits(32)(0), Bits(32)(0), Bits(32)(0), Bits(32)(0), Bits(32)(0))
    # log("{}", Opcode)
    res.if_change(Opcode == Bits(INST_WIDTH)(0b0110011), decode_typeR(v))
    res.if_change((Opcode == Bits(INST_WIDTH)(0b0010011)) | (Opcode == Bits(INST_WIDTH)(0b0000011)) | (Opcode == Bits(INST_WIDTH)(0b1100111)), decode_typeI(v))
    res.if_change(Opcode == Bits(INST_WIDTH)(0b0100011), decode_typeS(v))
    res.if_change(Opcode == Bits(INST_WIDTH)(0b1100011), decode_typeB(v))
    res.if_change(Opcode == Bits(INST_WIDTH)(0b1101111), decode_typeJ(v))
    res.if_change((Opcode == Bits(INST_WIDTH)(0b0010111)) | (Opcode == Bits(INST_WIDTH)(0b0110111)), decode_typeU(v))
    return res

class Fetcher(Module):
    def __init__(self):
        super().__init__({})

    @module.combinational
    def build(self, sram: SRAM):
        we = Bits(1)(0)
        re = ~we
        # re = Bits(1)(1)

        tick = RegArray(Bits(32), 1)
        (tick & self)[0] <= tick[0] + Bits(32)(1)

        log("tick = {}", tick[0])
        address_wire = tick[0]
        write_wire = Bits(INST_WIDTH)(0)

        val = RegArray(Bits(32), 1)
        log("we: {} | re: {} | addr: {} | dout: {}", we, re, address_wire, sram.dout[0])
        (val & self)[0] <= sram.dout[0]
        log('Got inst {}', val[0])

        decode_inst(sram.dout[0]).show()

        return we, re, address_wire, write_wire

        # tmp: Instruction = Inst(Bits(32)(1), Bits(32)(1), Bits(32)(1), Bits(32)(1), Bits(32)(1), Bits(32)(1))
        # tmp.show()
        # tmp.Type = Bits(32)(2)
        # tmp.show()
        # tmp.Type = Bits(32)(3)
        # tmp.show()
        # tmp.Type = Bits(32)(4)
        # tmp.show()
        # tmp.Type = Bits(32)(5)
        # tmp.show()
        # tmp.Type = Bits(32)(6)
        # tmp.show()
        # tmp.Type = Bits(32)(7)
        # tmp.show()