.section .text
.global _start

_start:
  li a0, 100
  sw a0, 4(x0)
  lw a1, 4(x0)
  sb x0, -1(x0)
