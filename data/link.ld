SECTIONS {
  . = 0x00000000;

  .text : { *(.text*) }
  .data : { *(.data*) }
  .bss  : { *(.bss*) }
}

MEMORY {
  text (rx)  : ORIGIN = 0x00000000, LENGTH = 4096M
  data (rw)  : ORIGIN = 0x80000000, LENGTH = 4096M
}
