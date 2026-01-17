from assassyn.frontend import *
from assassyn.backend import elaborate
from assassyn.utils import run_simulator, run_verilator

class RegArrays:
    def __init__(self, type, size, ego, init=None):
        self.size = size
        self.type = type
        if init:
            self.array = [RegArray(type, 1, [init[i]]) for i in range(size)]
        else:
            self.array = [RegArray(type, 1) for _ in range(size)]
        self.ego = ego

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.array[item][0]
        elif isinstance(item, Value):
            tmp = self.array[0][0]
            for i in range(self.size):
                tmp = (item == Bits(32)(i)).select(self.array[i][0], tmp)
            return tmp
        return None

    def __setitem__(self, key, value):
        if isinstance(key, int):
            (self.array[key] & self.ego)[0] <= value
        elif isinstance(key, Value):
            for i in range(self.size):
                with Condition(key == Bits(32)(i)):
                    (self.array[i] & self.ego)[0] <= value