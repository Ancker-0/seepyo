.section .text
.global _start

_start:
    sb      x0, -1(x0)     # Terminate and dump registers