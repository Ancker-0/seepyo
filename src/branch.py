from assassyn.frontend import *

def branch_predict(PC: Bits, label: Bits):
    return Int(32)(4) > label.bitcast(Int(32))