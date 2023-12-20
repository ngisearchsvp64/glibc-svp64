# SPDX-License-Identifier: LGPL-3-or-later
# Copyright 2023 VectorCamp
# Copyright 2023 Red Semiconductor Ltd.
#
# Funded by NGI Search Programme HORIZON-CL4-2021-HUMAN-01 2022,
# https://www.ngisearch.eu/, EU Programme 101069364.
    .machine libresoc
    .file   "strchr.c"
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
    .set s, 16
    .set t, 32
    .set addr0, 12
    .set addr1, 13

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

# Determine the string size - not given with the str* functions
.macro strlen rN, rS
    li                  \rN, 0
    # temp copy of pointer to str for determining length
    mr                  tmp, \rS
.check_len:
    lbz                 s, 0(tmp)
    cmpi                cr0, 1, s, 0
    addi                tmp, tmp, 1
    addi                \rN, \rN, 1
    bne                 cr0,.check_len
    # Saves having an extra label, perhaps not the best implementation...
    # need to have this if first char is NULL, meaning n=0
    subi                \rN, \rN, 1
.endm

    .globl __strchr
    .type   __strchr, @function
__strchr:
.LFB6:
    .cfi_startproc

    # Steps required for strchr
    # 1. Determine length of string, n
    # 2. Use the same algorithm for memchr, Horizontal-First version.

    # Load the character c into all bytes of register c64: GPR#7
    ori                 c64, c, 0
    ldbi                c64, tmp

    # Determine the length of string
    strlen              n, in_ptr

.outer:
    # Simple case: if bytes == 0, return NULL
    cmpldi              n, 0
    beq                 .tail

    # We should check for n <= 32
    cmpldi              n, 32
    blt                 .found

    # set up ctr to 4 64-bit elements (32 bytes)
    li                  ctr, 4 # using 1 for now, was 4
    li                  tmp, 5 # needs to be ctr+1, so that sv.bc will branch with CTR>0
.inner:
    # Create local in_ptr copies for Horizontal-First
    mr                  addr0, in_ptr
    setvl               0, 0, 3, 0, 1, 1 # VL=3
    sv.addi             *addr1, *addr0, 8

    setvl               0, ctr, 4, 0, 1, 1      # Set VL to 4 elements
    sv.ld               *s, 0(*addr0)           # Load from *in_ptr
    sv.cmpb             *t, *s, c64             # this will create a bitmask of FF where character c is found
    sv.cmpi             *cr0, 1, *t, 0
    # Counter needed for sv.bc, allows to determine which
    # doubleword has a matching char
    mtctr               tmp
    # Hard-coded instead of .determine_loc, binutils calculated
    # the wrong address of 0x88, which is bc instruction,
    # so get's stuck in infinite loop
    # To calculate the right constant, do make all,
    # then powerpc64le-linux-gnu-objdump -D svp64/strchr_svp64.o
    # To see the dump of the object file.
    # Take the address you want to get to (i.e. 0x98), subtract
    # the starting address of sv prefix for sv.bc (0x84),
    # the difference is the value to use (0x98-0x84=0x14).
    #sv.bc               0, *2, .determine_loc
    sv.bc               0, *2, 0x14
    addi                in_ptr, in_ptr, 32
    subi                n, n, 32

    b                   .outer

# At this point we know the matched character is within 32-bytes
# Now need to find which 8-byte doubleword.
.determine_loc:
    mfspr               ctr, 9 # Read current value of CTR reg
    li                  tmp, 4
    # 4-ctr will give the number of times 8 needs to be added
    # to in_ptr to get to the doubleword with matched char.
    sub                 tmp, tmp, ctr
    cmpi                cr0, 1, tmp, 0
    beq                 cr0, .found
    mtctr               tmp
.add_in_ptr:
    addi                in_ptr, in_ptr, 8
    #subi                n, n, 8
    bdnz                .add_in_ptr

.found:
    mtctr	            n                       # Set up counter
.found2:
    lbz                 s, 0(in_ptr)
    cmpw                cr0, c, s
    beqlr               cr0
    addi                in_ptr, in_ptr, 1
    bdnz                .found2

.tail:
    # If we have reached this point, there is no match, return NULL
    li                  res, 0
    blr
    .long 0
    .byte 0,0,0,0,0,0,0,0
    .cfi_endproc
.LFE6:
    .size   __strchr,.-__strchr
    .weak   strchr
    .hidden strchr
    .set    strchr,__strchr
    .ident  "GCC: (Debian 8.3.0-2) 8.3.0"
    .section    .note.GNU-stack,"",@progbits
