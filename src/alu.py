from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

from src.const import ROB_SIZE, INST_WIDTH
from instruction import Id_to_Instruction_Name

class ALU(Module):
    def __init__(self):
        super().__init__(ports = {
            "op_id": Port(Bits(INST_WIDTH)),
            "vj": Port(Bits(INST_WIDTH)),
            "vk": Port(Bits(INST_WIDTH)),
            "rob_id": Port(Bits(INST_WIDTH)),
        })

    @module.combinational
    def build(self, rob):
        with Condition(self.op_id.valid()):
            op_id = self.op_id.pop()
            vj = self.vj.pop()
            vk = self.vk.pop()
            rob_entry_id = self.rob_id.pop()  # ROB 条目号（0-7）

            # 只实现 Type R 的 add 指令 (op_id == 1)
            with Condition(op_id == Bits(32)(1)):
                result = vj + vk

                # 直接写回 ROB[rob_entry_id]（不需要遍历）
                rob.value[rob_entry_id] = result
                rob.busy[rob_entry_id] = Bits(1)(0)  # 标记为完成

                log("ALU: add executed, vj={}, vk={}, result={}, rob_entry={}", vj, vk, result, rob_entry_id)
