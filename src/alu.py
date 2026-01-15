from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

from rob import ROB
from src.const import ROB_SIZE, INST_WIDTH

class ALU(Module):
    def __init__(self):
        super().__init__(ports = {
            "op_id": Port(Bits(INST_WIDTH)),
            "vj": Port(Bits(INST_WIDTH)),
            "vk": Port(Bits(INST_WIDTH)),
            "rob_id": Port(Bits(INST_WIDTH)),
        })

    @module.combinational
    def build(self, rob: ROB, rs):
        with Condition(self.op_id.valid()):
            op_id = self.op_id.pop()
            vj = self.vj.pop()
            vk = self.vk.pop()
            fetch_id = self.rob_id.pop()  # ROB 条目号（0-7）

            # 实现 ALU 所有操作 (Type R: 1-10, Type I: 11-19, lui: 37)
            result = op_id.case({
                Bits(32)(1): vj + vk,      # add, addi
                Bits(32)(2): vj - vk,      # sub
                Bits(32)(3): vj & vk,      # and, andi
                Bits(32)(4): vj | vk,      # or, ori
                Bits(32)(5): vj ^ vk,      # xor, xori
                Bits(32)(6): vj << vk,     # sll, slli
                Bits(32)(7): vj >> vk,     # srl, srli
                Bits(32)(8): (vj.bitcast(Int(32)) >> vk).bitcast(Bits(32)),  # sra, srai
                Bits(32)(9): (vj.bitcast(Int(32)) < vk.bitcast(Int(32))).zext(Bits(32)),  # slt, slti
                Bits(32)(10): (vj < vk).zext(Bits(32)),  # sltu, sltiu
                Bits(32)(37): vk << Bits(32)(12),  # lui
                None: Bits(32)(0)
            })
            log("ALU: op_id={}, vj={}, vk={}, result={}, rob_entry={}", op_id, vj, vk, result, fetch_id)

            # 直接写回 ROB[rob_entry_id]（不需要遍历）
            rob_id = rob.entry_by_fetch_id(fetch_id)
            rob.value[rob_id] = result
            rob.busy[rob_id] = Bits(1)(0)  # 标记为完成

            # 广播到 RS，用于结果转发（result forwarding）
            # rs.rob_id.push(rob_entry_id)
            # rs.rob_value.push(result)

