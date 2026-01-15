from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

from register import Register
from src.const import ROB_SIZE, INST_WIDTH
from toolbox import  RegArrays
from instruction import Inst, inst_id_to_type, get_int_val

class ROB(Module):
    def __init__(self, robL, robR):
        super().__init__(ports = {
            "rd": Port(Bits(INST_WIDTH)),
            "rs1": Port(Bits(INST_WIDTH)),
            "rs2": Port(Bits(INST_WIDTH)),
            "imm": Port(Bits(INST_WIDTH)),
            "Type": Port(Bits(INST_WIDTH)),# Type 是指令种类的 type
            "Id": Port(Bits(INST_WIDTH)),# Id 是指令类型的 ID
            "expect_value": Port(Bits(INST_WIDTH)),
            "branch_PC": Port(Bits(INST_WIDTH)),
            "Fetch_id": Port(Bits(INST_WIDTH)),# 读进来给的 id
        })

        self.size = ROB_SIZE
        self.busy = RegArrays(Bits(1), ROB_SIZE, self) # 是否已经算好了
        self.Op_id = RegArrays(Bits(32), ROB_SIZE, self)
        self.dest = RegArrays(Bits(32), ROB_SIZE, self)
        self.value = RegArrays(Bits(32), ROB_SIZE, self)
        self.expect_val = RegArrays(Bits(32), ROB_SIZE, self)  # 重命名避免与端口冲突
        self.branch_pc_val = RegArrays(Bits(32), ROB_SIZE, self)  # 重命名避免与端口冲突
        self.fetch_id = RegArrays(Bits(32), ROB_SIZE, self)
        self.is_terminate = RegArrays(Bits(1), ROB_SIZE, self)
        # self.L = RegArray(Bits(32), 1, [0])
        # self.R = RegArray(Bits(32), 1, [0])
        self.L = robL
        self.R = robR

        self.flush_tag = RegArrays(Bits(1), 1, self)

    def rob_clean_one(self, pos):
        self.busy[pos] = Bits(1)(0)
        self.Op_id[pos] = Bits(32)(0)
        self.dest[pos] = Bits(32)(0)
        self.value[pos] = Bits(32)(0)
        self.fetch_id[pos] = Bits(32)(0)
        self.expect_val[pos] = Bits(32)(0)
        self.branch_pc_val[pos] = Bits(32)(0)

    def rob_clear(self):
        for i in range(ROB_SIZE):
            self.rob_clean_one(i)

    def rob_push(self, Op_id, dest, value, ID, expect_value, branch_PC, busy: bool = True):
        # 更新 R 指针（先读取当前值，计算新值，然后写回）
        entry = self.R[0]  # 当前 R[0] 就是要分配的条目索引
        new_R = (self.R[0] + Bits(32)(1)) % Bits(32)(ROB_SIZE)
        self.R[0] = new_R
        log("pushed to {}", entry)

        self.busy[entry] = Bits(1)(busy)
        self.Op_id[entry] = Op_id
        self.dest[entry] = dest
        self.value[entry] = value
        self.fetch_id[entry] = ID
        self.expect_val[entry] = expect_value
        self.branch_pc_val[entry] = branch_PC
        return entry  # 返回分配的条目索引

    def rob_push_store(self, Op_id, dest, value, ID, expect_value, branch_PC, is_terminate):
        # For store instructions - same as rob_push but sets =0
        # since stores don't execute in ALU
        entry = self.R[0]
        new_R = (self.R[0] + Bits(32)(1)) % Bits(32)(ROB_SIZE)
        self.R[0] = new_R
        log("store pushed to {}", entry)

        self.busy[entry] = Bits(1)(0)  # Store entries start as not busy
        self.Op_id[entry] = Op_id
        self.dest[entry] = dest
        self.value[entry] = value
        self.fetch_id[entry] = ID
        self.expect_val[entry] = expect_value
        self.branch_pc_val[entry] = branch_PC
        self.is_terminate[entry] = is_terminate
        return entry

    def rob_pop(self):
        # 使用当前的 L[0] 清理条目
        entry_idx = self.L[0]
        log("rob_pop entry {}", self.L[0])
        self.rob_clean_one(entry_idx)

        # 更新 L 指针（时序写入，下一个周期生效）
        (self.L & self)[0] <= (entry_idx + Bits(32)(1)) % Bits(32)(ROB_SIZE)
    
    def qfull(self):
        # For some technical reasons, the modification from fetcher takes two cycles to take effect in rob,
        # which means we need to leave one space for this.
        return ((self.R[0] + Bits(32)(1)) % Bits(32)(ROB_SIZE) == self.L[0]) | ((self.R[0] + Bits(32)(2)) % Bits(32)(ROB_SIZE) == self.L[0])

    def log(self):
        log("------- ROB log start ------- L={}, R={}", self.L[0], self.R[0])
        for i in range(self.size):
            log("Busy = {}, Op_id = ${}$, dest = {}, value {}, expect_value = {}, branch_PC = {}, ID = {}, term = {}", self.busy[i],
                self.Op_id[i], self.dest[i], self.value[i], self.expect_val[i], self.branch_pc_val[i], self.fetch_id[i],
                self.is_terminate[i])
        log("------- ROB log end -------")

    def entry_by_fetch_id(self, fetch_id: Bits):
        ret = Bits(32)(0)
        for i in range(ROB_SIZE):
            ret = (self.fetch_id[i] == fetch_id).select(Bits(32)(i), ret)
        return ret

    @module.combinational
    def build(self, rf: Register, rs):
        with Condition(self.flush_tag[0]):
            log("branch mispredict happened, flushing ROB and rf")
            self.L[0] = Bits(32)(0)
            self.R[0] = Bits(32)(0)
            self.flush_tag[0] = Bits(1)(0)
            rf.clear_dependence()
            self.rob_clear()
            for port in self.ports:
                with Condition(port.valid()):
                    port.pop()

        with Condition(~self.flush_tag[0]):
            new_dest = self.rd.valid().select(self.rd.peek(), Bits(32)(0))
            # 如果当前要修改的值和提交要求改的值是同一个地方，就不用改提交的修改了

            with Condition(self.rd.valid()):
                # done things for ROB
                inst = Inst(self.rd.pop(), self.rs1.pop(), self.rs2.pop(), self.imm.pop(), self.Type.pop(), self.Id.pop())
                inst.show()
                expect_value = self.expect_value.pop()
                branch_PC = self.branch_PC.pop()
                Fetch_id = self.Fetch_id.pop()

                with Condition((inst.Type == Bits(32)(1)) | (inst.Type == Bits(32)(2))):
                    log("ROB: Type {}/{}, updating rf.dependence[{}] = {}", inst.Type, inst.id, inst.rd, Fetch_id)
                    rf.update(inst.rd, rf.val[inst.rd], Fetch_id)
                    self.rob_push(inst.id, inst.rd, Bits(32)(0), Fetch_id, expect_value, branch_PC)
                with Condition(inst.Type == Bits(32)(4)):
                    self.rob_push(inst.id, Bits(32)(0), Bits(32)(0), Fetch_id, expect_value, branch_PC)
                with Condition(inst.Type == Bits(32)(3)):
                    # Type S (store) - allocate ROB entry for store instructions
                    # Use rob_push_store which sets Busy=0 (stores don't execute in ALU)
                    is_terminate = (inst.id == Bits(32)(25)) & (inst.rs1 == Bits(32)(0)) & (inst.rs2 == Bits(32)(0)) & (inst.imm == Bits(32)(0xFFFFFFFF))
                    self.rob_push_store(inst.id, Bits(32)(0), Bits(32)(0), Fetch_id, expect_value, branch_PC, is_terminate)
                with Condition(inst.Type == Bits(32)(5)):  # type-J: only jal
                    rf.update(inst.rd, inst.imm, Fetch_id)
                    self.rob_push(inst.id, inst.rd, inst.imm, Fetch_id, expect_value, branch_PC, busy=False)
                # Type 0 (invalid) instructions are not pushed to ROB
                # They represent decoded 0x00000000 or other invalid encodings

            # need to deal with ALU so that we can commit
            # TODO

            # commit
            commit_inst_type = inst_id_to_type(self.Op_id[self.L[0]])
            top_ready = (self.L[0] != self.R[0]) & (~self.busy[self.L[0]])
            predict_failed = ((commit_inst_type == Bits(32)(4)) | (commit_inst_type == Bits(32)(6))) & (self.expect_val[self.L[0]] != self.value[self.L[0]])

            with Condition(top_ready):
                Commit_id = self.fetch_id[self.L[0]]
                log("Committing inst id = {}, value = {}", Commit_id, self.value[self.L[0]])

                # in case of branch mispredict
                with Condition(predict_failed):
                    rs.flush_tag.push(Bits(1)(1))
                    # need more TODO with memory access
                    self.flush_tag[0] = Bits(1)(1) # for register, we need one clock lag to flush for register is a downstream module in code but instead need one clock

                # show to rf
                with Condition((commit_inst_type == Bits(32)(1)) | (commit_inst_type == Bits(32)(2))):
                    dest = self.dest[self.L[0]]
                    with Condition(dest != new_dest):
                        with Condition((rf.dependence[dest] == Commit_id)):
                            rf.update(dest, self.value[self.L[0]], Bits(32)(0))
                            log("commit rf[{}] = {}", dest, self.value[self.L[0]])

                # show to rs
                rs.rob_id.push(Commit_id)
                rs.rob_value.push(self.value[self.L[0]])

                # Check for termination
                with Condition(self.is_terminate[self.L[0]]):
                    log("=== PROGRAM TERMINATION: sb x0, -1(x0) ===")
                    log("Register dump:")
                    rf.show()

                self.rob_pop()

        self.log()