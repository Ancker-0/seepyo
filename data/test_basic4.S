.section .text
.global _start

_start:
  addi a0, x0, -1
  sb x0, -1(x0)
