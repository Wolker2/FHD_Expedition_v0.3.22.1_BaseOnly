SECTIONS { .dosstub 0 : { *(.dosstub) } .text 0x10001000 : { *(.text) } .data 0x10003000 : { *(.data) } /DISCARD/ : { *(.note*) *(.comment*) } }
