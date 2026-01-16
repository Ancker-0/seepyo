# Expected result:
# a1: 10
# a2: 20
# ra: 200

.section .text
.global _start

_start:
  li a1, 10
  li a2, 20
  beq a1, a2, then
  li ra, 200
  jal x0, fi
then:
  li ra, 100
fi:
  sb      x0, -1(x0)     # Terminate and dump registers
