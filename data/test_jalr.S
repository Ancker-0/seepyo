.section .text
.global _start

_start:
  jalr x1, x0, 8
  sb x0, -1(x0)

C:
  ret
