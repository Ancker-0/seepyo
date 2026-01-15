.section .text
.global _start

_start:
  sw t1, 0(t2)
  add t2, t1, sp
  andi t1, t1, 5
  jalr sp, a0, 1052
  jal ra, 5050
  lb a1, 5(a2)
  li a1, 5
  ret
  slti sp, t1, 5
  add a1, a2, a3
  li a0, 2000
  li a2, 1
  li t0, 1
  li t1, 1
  slli t0, t0, 2
  slli t1, t1, 1
  srli t0, t0, 1
  sll t0, t0, a2
  srl t1, t1, a2
  slli t1, t1, 2
  slt a1, a0, t0
  blt a1, a2, -28
  add sp, sp, a0
  add sp, sp, a1
  add sp, sp, a2
  add sp, sp, t0
  add sp, sp, t1
  sb x0, -1(x0)
