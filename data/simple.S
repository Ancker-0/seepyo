.section .text
.global _start

_start:
  lui sp, 2
  jal main
  sb x0, -1(x0)

main:
  add sp, sp, -16
  sw ra, 12(sp)
  lw a0, 12(sp)
  ret
