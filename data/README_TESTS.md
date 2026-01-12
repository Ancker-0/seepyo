# 测试数据说明

## 测试文件

### test_arithmetic.data
基本的算术运算测试，包含以下指令序列：

| 地址 | 指令 | 说明 | 预期结果 |
|------|------|------|----------|
| 0 | `add x1, x0, x0` | x1 = 0 + 0 | x1 = 0 |
| 1 | `lui x2, 0x1000` | 加载立即数 | x2 = 0x1000 |
| 2 | `lui x3, 0x2000` | 加载立即数 | x3 = 0x2000 |
| 3 | `add x4, x2, x3` | x4 = x2 + x3 | x4 = 0x3000 |
| 4 | `addi x5, x0, 10` | x5 = 0 + 10 | x5 = 10 |
| 5 | `addi x6, x5, 20` | x6 = 10 + 20 | x6 = 30 |
| 6 | `addi x7, x6, -5` | x7 = 30 + (-5) | x7 = 25 |
| 7 | `and x8, x5, x6` | x8 = 10 & 30 | x8 = 10 |
| 8 | `or x9, x5, x6` | x9 = 10 \| 30 | x9 = 30 |
| 9 | `xor x10, x5, x6` | x10 = 10 ^ 30 | x10 = 20 |
| 10 | `lui x11, 0xFFFFF` | 负数加载 | x11 = 0xFFFFF000 |
| 11 | `add x12, x11, x11` | x12 = x11 + x11 | x12 = 0xFFFFE000 |
| 12 | `andi x13, x11, 0xFFF` | x13 = x11 & 0xFFF | x13 = 0 |
| 13 | `ori x14, x0, 0xFF` | x14 = 0 \| 0xFF | x14 = 0xFF |
| 14+ | `nop` | 空操作 | - |

### test_comprehensive.data
更全面的测试，包含更多指令类型的组合：

| 指令 | 说明 |
|------|------|
| `lui x1-x4` | 初始化寄存器 x1=0x1000, x2=0x2000, x3=0x3000, x4=0xA000 |
| `add` 组 | 测试寄存器加法 |
| `and` 组 | 测试按位与运算 |
| `or` 组 | 测试按位或运算 |
| `xor` 组 | 测试按位异或运算 |
| `addi` 组 | 测试立即数加法（正数、负数） |
| `andi` 组 | 测试立即数按位与 |
| `ori` 组 | 测试立即数按位或 |
| `xori` 组 | 测试立即数按位异或 |

## 使用方法

### 方法一：直接使用测试文件
修改 `src/main.py` 或相关代码，将 SRAM 初始化文件改为相应的测试文件：
```python
sram = SRAM(Bits(INST_WIDTH), 2**ADDR_WIDTH, "data/test_arithmetic.data")
# 或
sram = SRAM(Bits(INST_WIDTH), 2**ADDR_WIDTH, "data/test_comprehensive.data")
```

### 方法二：重新生成测试数据
```bash
cd data && python simple_tests.py
```

## 指令编码参考

### R 类型指令格式
```
|31    25|24   20|19   15|14  12|11   7|6     0|
| funct7 |  rs2  |  rs1  |funct3|  rd  |opcode|
```

- `add`: funct7=0000000, funct3=000, opcode=0110011
- `sub`: funct7=0100000, funct3=000, opcode=0110011
- `and`: funct7=0000000, funct3=111, opcode=0110011
- `or`:  funct7=0000000, funct3=110, opcode=0110011
- `xor`: funct7=0000000, funct3=100, opcode=0110011

### I 类型指令格式
```
|31        20|19   15|14  12|11   7|6     0|
|   imm11_0  |  rs1  |funct3|  rd  |opcode|
```

- `addi`: funct3=000, opcode=0010011
- `andi`: funct3=111, opcode=0010011
- `ori`:  funct3=110, opcode=0010011
- `xori`: funct3=100, opcode=0010011

### U 类型指令格式
```
|31             12|11   7|6     0|
|     imm31_12    |  rd  |opcode|
```

- `lui`:   opcode=0110111
- `auipc`: opcode=0010111
