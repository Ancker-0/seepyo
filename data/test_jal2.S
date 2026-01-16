# Expect: ra = 20, a0 = 20, a1 = 40

.section .text
.global _start

_start:
  jal A
  li a0, 100
  A:
  li a0, 200
  sb      x0, -1(x0)     # Terminate and dump registers
