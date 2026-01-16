# Expected result:
# x10: 100
# x11: 10
# x12: 10
# x13: 155

.section .text
.global _start

_start:
  li a0, 100
  li a1, 0
  li a2, 10
  add a3, a0, a2
loop:
  beq a1, a2, done
  add a3, a3, a1
  addi a1, a1, 1
  jal x0, loop
done:
  sb      x0, -1(x0)     # Terminate and dump registers
