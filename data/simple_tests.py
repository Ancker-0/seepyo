"""
生成简单的 RISC-V 测试指令
用于测试基本的算术运算

指令编码格式参考：
- Type R: funct7(31-25) | rs2(24-20) | rs1(19-15) | funct3(14-12) | rd(11-7) | opcode(6-0)
  opcode = 0b0110011

- Type I: imm11_0(31-20) | rs1(19-15) | funct3(14-12) | rd(11-7) | opcode(6-0)
  opcode = 0b0010011

- Type U: imm31_12(31-12) | rd(11-7) | opcode(6-0)
  lui opcode = 0b0110111
  auipc opcode = 0b0010111
"""

def encode_r_type(funct7, rs2, rs1, funct3, rd, opcode=0b0110011):
    """编码 R 类型指令"""
    instr = 0
    instr |= (funct7 & 0x7F) << 25
    instr |= (rs2 & 0x1F) << 20
    instr |= (rs1 & 0x1F) << 15
    instr |= (funct3 & 0x7) << 12
    instr |= (rd & 0x1F) << 7
    instr |= (opcode & 0x3F)
    return instr

def encode_i_type(imm, rs1, funct3, rd, opcode=0b0010011):
    """编码 I 类型指令"""
    instr = 0
    instr |= (imm & 0xFFF) << 20
    instr |= (rs1 & 0x1F) << 15
    instr |= (funct3 & 0x7) << 12
    instr |= (rd & 0x1F) << 7
    instr |= (opcode & 0x3F)
    return instr

def encode_u_type(imm, rd, opcode):
    """编码 U 类型指令"""
    instr = 0
    instr |= (imm & 0xFFFFF000)  # imm[31:12]
    instr |= (rd & 0x1F) << 7
    instr |= (opcode & 0x3F)
    return instr

def generate_arithmetic_test():
    """生成基本算术运算测试"""
    instructions = []

    # 测试 1: add 指令
    # add x1, x0, x0  (x1 = x0 + x0 = 0)
    instructions.append(encode_r_type(0b0000000, 0, 0, 0b000, 1))

    # 测试 2: 使用 lui 加载立即数到寄存器
    # lui x2, 0x00001  (x2 = 0x1000)
    instructions.append(encode_u_type(0x1000, 2, 0b0110111))

    # lui x3, 0x00002  (x3 = 0x2000)
    instructions.append(encode_u_type(0x2000, 3, 0b0110111))

    # 测试 3: add x4, x2, x3  (x4 = 0x1000 + 0x2000 = 0x3000)
    instructions.append(encode_r_type(0b0000000, 3, 2, 0b000, 4))

    # 测试 5: addi x5, x0, 10  (x5 = 0 + 10 = 10)
    instructions.append(encode_i_type(10, 0, 0b000, 5))

    # 测试 6: addi x6, x5, 20  (x6 = 10 + 20 = 30)
    instructions.append(encode_i_type(20, 5, 0b000, 6))

    # 测试 7: addi x7, x6, -5  (x7 = 30 + (-5) = 25)
    instructions.append(encode_i_type(-5 & 0xFFF, 6, 0b000, 7))

    # 测试 8: and x8, x5, x6  (x8 = 10 & 30 = 10)
    instructions.append(encode_r_type(0b0000000, 6, 5, 0b111, 8))

    # 测试 9: or x9, x5, x6  (x9 = 10 | 30 = 30)
    instructions.append(encode_r_type(0b0000000, 6, 5, 0b110, 9))

    # 测试 10: xor x10, x5, x6  (x10 = 10 ^ 30 = 20)
    instructions.append(encode_r_type(0b0000000, 6, 5, 0b100, 10))

    # 测试 11: lui x11, 0xFFFFF  (x11 = 0xFFFFF000, 负数测试)
    instructions.append(encode_u_type(0xFFFFF000, 11, 0b0110111))

    # 测试 12: add x12, x11, x11  (x12 = 0xFFFFF000 + 0xFFFFF000)
    instructions.append(encode_r_type(0b0000000, 11, 11, 0b000, 12))

    # 测试 13: andi x13, x11, 0xFFF  (x13 = 0xFFFFF000 & 0xFFF = 0)
    instructions.append(encode_i_type(0xFFF, 11, 0b111, 13))

    # 测试 14: ori x14, x0, 0xFF  (x14 = 0 | 0xFF = 0xFF)
    instructions.append(encode_i_type(0xFF, 0, 0b110, 14))

    # 填充剩余空间为 nop (add x0, x0, x0)
    while len(instructions) < 2**12:
        instructions.append(encode_r_type(0b0000000, 0, 0, 0b000, 0))

    return instructions

def generate_comprehensive_test():
    """生成更全面的测试，包含更多指令类型"""
    instructions = []

    # 初始化一些寄存器
    # lui x1, 0x00001
    instructions.append(encode_u_type(0x1000, 1, 0b0110111))
    # lui x2, 0x00002
    instructions.append(encode_u_type(0x2000, 2, 0b0110111))
    # lui x3, 0x00003
    instructions.append(encode_u_type(0x3000, 3, 0b0110111))
    # lui x4, 0x0000A
    instructions.append(encode_u_type(0xA000, 4, 0b0110111))

    # add 指令测试
    # add x5, x1, x2
    instructions.append(encode_r_type(0b0000000, 2, 1, 0b000, 5))
    # add x6, x3, x4
    instructions.append(encode_r_type(0b0000000, 4, 3, 0b000, 6))

    # and 指令测试
    # and x7, x1, x2
    instructions.append(encode_r_type(0b0000000, 2, 1, 0b111, 7))
    # and x8, x5, x6
    instructions.append(encode_r_type(0b0000000, 6, 5, 0b111, 8))

    # or 指令测试
    # or x9, x1, x2
    instructions.append(encode_r_type(0b0000000, 2, 1, 0b110, 9))
    # or x10, x5, x6
    instructions.append(encode_r_type(0b0000000, 6, 5, 0b110, 10))

    # xor 指令测试
    # xor x11, x1, x2
    instructions.append(encode_r_type(0b0000000, 2, 1, 0b100, 11))
    # xor x12, x5, x6
    instructions.append(encode_r_type(0b0000000, 6, 5, 0b100, 12))

    # addi 指令测试
    # addi x13, x0, 100
    instructions.append(encode_i_type(100, 0, 0b000, 13))
    # addi x14, x13, 50
    instructions.append(encode_i_type(50, 13, 0b000, 14))
    # addi x15, x13, -20
    instructions.append(encode_i_type(-20 & 0xFFF, 13, 0b000, 15))

    # andi 指令测试
    # andi x16, x13, 0xFF
    instructions.append(encode_i_type(0xFF, 13, 0b111, 16))
    # andi x17, x14, 0xF0
    instructions.append(encode_i_type(0xF0, 14, 0b111, 17))

    # ori 指令测试
    # ori x18, x0, 0x80
    instructions.append(encode_i_type(0x80, 0, 0b110, 18))
    # ori x19, x16, 0x0F
    instructions.append(encode_i_type(0x0F, 16, 0b110, 19))

    # xori 指令测试
    # xori x20, x18, 0xFF
    instructions.append(encode_i_type(0xFF, 18, 0b100, 20))

    # 填充剩余空间为 nop
    while len(instructions) < 2**12:
        instructions.append(encode_r_type(0b0000000, 0, 0, 0b000, 0))

    return instructions

def write_test_file(filename, instructions):
    """将指令写入测试文件"""
    with open(filename, "w") as f:
        for instr in instructions:
            f.write(f"{instr:08x}\n")

def main():
    print("生成基本算术测试...")
    arithmetic_instructions = generate_arithmetic_test()
    write_test_file("data/test_arithmetic.data", arithmetic_instructions)
    print(f"已生成 {len(arithmetic_instructions)} 条指令到 data/test_arithmetic.data")

    print("\n生成综合测试...")
    comprehensive_instructions = generate_comprehensive_test()
    write_test_file("data/test_comprehensive.data", comprehensive_instructions)
    print(f"已生成 {len(comprehensive_instructions)} 条指令到 data/test_comprehensive.data")

    # 打印前几条指令的详细信息
    print("\n=== test_arithmetic.data 前 15 条指令 ===")
    for i, instr in enumerate(arithmetic_instructions[:15]):
        print(f"Addr {i:3d}: 0x{instr:08x}")

    print("\n=== test_comprehensive.data 前 20 条指令 ===")
    for i, instr in enumerate(comprehensive_instructions[:20]):
        print(f"Addr {i:3d}: 0x{instr:08x}")

if __name__ == "__main__":
    main()
