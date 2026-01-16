.section .text
.global _start

_start:
  li x0, 1
  li x0, 2
  li x0, 3
  li x0, 4
  li x0, 5
  li a1, 2
  add x0, x0, a1
  sb      x0, -1(x0)     # Terminate and dump registers
