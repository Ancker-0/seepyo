.section .text
.global _start

_start:
  lw a0, 1(x0)
  sb x0, -1(x0)
