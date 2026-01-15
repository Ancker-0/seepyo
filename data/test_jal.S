# Expect: ra = 20, a0 = 20, a1 = 40

.section .text
.global _start

_start:
beg:
  jal A
  jal beg
  li a0, 10
A:
  li a0, 20
  jal C
B:
  li a0, 30
  jal beg
C:
  li a1, 40
  sb      x0, -1(x0)     # Terminate and dump registers
