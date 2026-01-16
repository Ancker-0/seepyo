# a0 = 4096
# a1 = -4096
.section .text
.global _start

_start:
  lui a0, 1
  lui a1, 1048575
  sb x0, -1(x0)
