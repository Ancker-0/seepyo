.section .text
.global _start

_start:
    li      a0, 100        # Initialize a0 (x10) = 100
    li      a1, 200        # Initialize a1 (x11) = 200
    add     a2, a0, a1     # a2 (x12) = a0 + a1 = 300
    li      t0, 42         # t0 (x5) = 42
    sb      x0, -1(x0)     # Terminate and dump registers
