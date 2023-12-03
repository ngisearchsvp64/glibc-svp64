    .machine libresoc
    .file   "memchr.c"
    .abiversion 2
    .section   ".text"
    .align 2

    .set in_ptr, 3
    .set res, 3
    .set c, 4
    .set n, 5
    .set tmp, 6
    .set ctr, 7
    .set c64, 8
    .set c_01, 9
    .set c_80, 10
    .set c_ff, 1
    .set s, 16
    .set t, 32

# Helper macros

# load & duplicate byte to a 64-bit register, tmp register passed
.macro  ldbi rD, rT
    rldicr  \rT,\rD,8,55
    or      \rT,\rT,\rD
    rldicr  \rD,\rT,16,47
    or      \rD,\rD,\rT
    rldicr  \rT,\rD,32,31
    or      \rD,\rT,\rD
.endm

    .globl __memchr
    .type   __memchr, @function
__memchr:
.LFB6:
    .cfi_startproc

    # Steps required for memchr
    # 1. First we need to get the SIZE = min(n, 32).
    # 2. Then the outer loop will try to process up to SIZE bytes and reduce SIZE by 64.
    # Outer loop will run until SIZE = 0.
    # 3. The inner loop can be a modified (sans the store) version of this:
    # https://git.libre-soc.org/?p=openpower-isa.git;a=blob;f=src/openpower/decoder/isa/test_caller_svp64_ldst.py;h=4ecf534777a5e8a0178b29dbcd69a1a5e2dd14d6;hb=HEAD#l36
    #

    # Load the character c into all bytes of register c64: GPR#7
    ori                 c64, c, 0
    ldbi                c64, tmp
    # Start from the end - TODO: li is 16-bit I think, probably will fail if n too big...
    # Need to subtract 1 as memory index starts at 0 for n=1, etc.
    add					in_ptr, in_ptr, n
    subi				in_ptr, in_ptr, 1

.outer:
    # Simple case: if bytes == 0, return NULL
    cmpldi              n, 0
    beq                 .tail

    # We should check for n <= 32
    cmpldi              n, 32
    blt                 .found

	# TODO: Messy...this offset only needs to happen once
	# at the start. As we're starting at the end and
	# reading 8 bytes at a time, need to go back by 7 bytes
	# Skip if not the first iteration
	cmpi				cr0, 0, ctr, 0
	bf					2, .skip_offset
	subi				in_ptr, in_ptr, 7
.skip_offset:
    # set up ctr to 4 64-bit elements (32 bytes)
    li                  ctr, 1 # using 1 for now, was 4
    mtctr               ctr
    setvl               0, ctr, 4, 1, 1, 1      # Set VL to 4 elements, VF=1
.inner:
    sv.ld               *s, 0(in_ptr)           # Load from *in_ptr
    sv.cmpb             *t, *s, c64             # this will create a bitmask of FF where character c is found
    sv.cmpi             *cr0, 1, *t, 0
    # Hard-coded instead of .found, binutils calculated
    # the wrong address of 0x68, which is bc instruction,
    # so get's stuck in infinite loop
    # To calculate the right constant, do make all,
    # then powerpc64le-linux-gnu-objdump -D svp64/memrchr_svp64.o
    # To see the dump of the object file.
    # Take the address you want to got (i.e. 0x80), subtract
    # the starting address of sv prefix for sv.bc (0x64),
    # the difference is the value to use (0x80-0x64=0x1c).
    #sv.bc               4, *2, .found
    sv.bc               4, *2, 0x1c
    svstep              0, 1, 0
    subi                in_ptr, in_ptr, 8
    subi                n, n, 8
    #sv.bc/all           16, *cr0, .found
    # alternatively could checked the overflow bit of CR0...
    bdnz                .inner # or alternatively, bc 16, 0, .inner

    b                   .outer


.found:
    mtctr	            n                       # Set up counter
.found2:
    lbz                 s, 0(in_ptr)
	cmpw                cr0, c, s
	beqlr               cr0
	subi                in_ptr, in_ptr, 1
	bdnz                .found2

.tail:
    # If we have reached this point, there is no match, return NULL
	li                  res, 0
    blr
    .long 0
    .byte 0,0,0,0,0,0,0,0
    .cfi_endproc
.LFE6:
    .size   __memchr,.-__memchr
    .weak   memchr
    .hidden memchr
    .set    memchr,__memchr
    .ident  "GCC: (Debian 8.3.0-2) 8.3.0"
    .section    .note.GNU-stack,"",@progbits
