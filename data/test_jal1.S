# ra: 12
# a0: 100

.section .text
.global _start

_start:
    jal B
    sb x0, -1(x0)
    A:
    jal C

    B:
    jal A

    C:
    li a0, 100
    sb x0, -1(x0)
