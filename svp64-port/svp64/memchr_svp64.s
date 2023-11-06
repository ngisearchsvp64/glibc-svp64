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
    .set d, 48
    .set t, 96

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

# check if 64-bit word has a zero byte
# #define haszero(v) (((v) - 0x01010101UL) & ~(v) & 0x80808080UL)
.macro  haszero rD, rS, rT, c_01_, c_80_
    subf        \rT, \c_01_, \rS
    andc        \rD, \rT, \rS
    and         \rD, \rT, \c_80_
    cmpli       \rD, 0
.endm

#SVP64 version
.macro  sv_haszero rD, rS, rT, c_01_, c_80_, jumpto
    sv.subf     *\rT, \c_01_, *\rS
    sv.andc     *\rD, *\rT, *\rS
    sv.and      *\rD, *\rT, \c_80_
    sv.cmpi     *cr0, 0, *\rD, 0
    sv.bc       *cr0, 2, \jumpto
.endm

# check if 64-bit word has a char c, just xor the word with c64 and call haszero
.macro  haschar rD, rS, rT, c64_, c_01_, c_80_
    xor         \rD, \c64_, \rD
    haszero     \rD, \rS, \rT, \c_01_, \c_80_
.endm

#SVP64 version
.macro  sv_haschar rD, rS, rT, c64_, c_01_, c_80_, jumpto
    sv.xor      *\rD, \c64_, *\rD
    sv_haszero  \rD, \rS, \rT, \c_01_, \c_80_, \jumpto
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

    # Simple case: if bytes == 0, return NULL
    cmpldi              n, 0
    beq                 .tail

    # We should check for n <= 8
    cmpldi              n, 8
    blt                 .found

    # We have to check for alignment
	andi.               tmp, in_ptr, 0x7
	beq                 .aligned

    mtctr	            tmp                       # Set up counter
.head:
    lbz                 s, 0(in_ptr)
	cmpw                cr0, c, s
	beqlr               cr0
	addi                in_ptr, in_ptr, 1
    subi                n, n, 1
	bdnz                .head

.aligned:
    # We should check for n <= 8
    cmpldi              n, 8
    blt                 .found

    # Size is >= 8
    # Load the character c into all bytes of register c64: GPR#7
    ori                 c64, c, 0
    ldbi                c64, tmp
    
    # Load the constants 0x0101010101010101ULL and 0x8080808080808080ULL for zero byte check
    li                  c_01, 0x01
    ldbi                c_01, tmp
    sldi                c_80, c_01, 7
    li                  c_ff, 0xff
    ldbi                c_ff, tmp
           
.outer:
    # find out how many bytes to load from s: min(n, 32), but in octets
    srdi                tmp, n, 3
    cmpldi              tmp, 4
    blt                 .inner
    li                  tmp, 4

.inner:
    # Set ctr to min(32, n)
    ori                 ctr, tmp, 0

    setvl               0, 0, ctr, 0, 1, 1      # Set VL to 4 elements
    #setvl               0, 0, ctr, 1, 1, 1      # MAXVL=VL=4, VF=1
    sv.ld               *s, 0(in_ptr)           # Load from *in_ptr
    #sv_haschar          d, s, t, c64, c_01, c_80, .found
    sv.cmpb             *t, *s, c64
    sv.cmp              *cr0, 0, *t, 1
    sv.bc               *cr0, 2, .found
    #sv.cmp/ff=ne/vli    *cr0, c64, *s, 1        # cmp against mask, truncate VL
    #svstep.             ctr, 1, 0               # step to next in-regs element
    #bc                  6, 3, .inner               # svstep. Rc=1 loop-end-condition?
    addi                in_ptr, in_ptr, 32
    subi                n, n, 32
    cmplwi              n, 0
    bne                 .outer
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
    .size   __memchr,.-__memchr
    .weak   memchr
    .hidden memchr
    .set    memchr,__memchr
    .ident  "GCC: (Debian 8.3.0-2) 8.3.0"
    .section    .note.GNU-stack,"",@progbits
