.section .text
.global _start

_start:
  lui sp, 2
  jal main
  sb x0, -1(x0)

main:
  li a1, 0
  li a2, 0
begin:
  add a2, a1, a2
  addi a1, a1, 1
  li a3, 9
  bge a3, a1, begin
  ret
