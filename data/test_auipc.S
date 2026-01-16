# a0 = 100
# a1 = 4100
# a2 = -4088
.section .text
.global _start

_start:
  li a0, 100
  auipc a1, 1
  auipc a2, 1048575
  sb x0, -1(x0)
