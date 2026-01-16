# a0 = 1
# a1 = -1
# a3 = 2097151
# t0 = x5 = 1
# ra = 32

.section .text
.global _start

_start:
  li a0, 1
  li a1, 20
  li a3, 0

begin:
  blt a1, x0, end
  sll t0, a0, a1
  add a3, a3, t0
  addi a1, a1, -1
  jal begin

end:
  sb x0, -1(x0)
