# SPDX-License-Identifier: LGPL-3-or-later
# Copyright 2023 VectorCamp
# Copyright 2023 Red Semiconductor Ltd.
#
# Funded by NGI Search Programme HORIZON-CL4-2021-HUMAN-01 2022,
# https://www.ngisearch.eu/, EU Programme 101069364.
    .machine libresoc
    .file   "vperm.c"
    .abiversion 2
    .section   ".text"
    .align 2

    # Assigned register numbers:
    # vec1    -> r3, r4
    # vec2    -> r5, r6
    # vec3    -> r7, r8
    # res     -> r9, r10
    # mask0   -> r11
    # mask1   -> r12
    # maskOut -> r13, r14
    # tmp     -> r15

    .set vec1, 3
    .set vec2, 5
    .set vec3, 7
    # Not sure where whether we want to overwrite one of the vectors,
    # I'm assuming result should be stored somewhere else.
    .set res, 9
    # Mask for when vec3 is set to vec1 (0x0000_0000_0000_0000)
    # Mask for when vec3 is set to vec2 (0x0101_0101_0101_0101)
    # Only need single register because mask can be reused between lower
    # and upper 8 bytes.
    .set mask0, 11
    .set mask1, 12
    # Mask which will be created based on comparison of vec3 with
    # mask0 and mask1. Will be 16 bytes long, so needs 2 registers
    # maskOut -> r13,r14
    .set maskOut, 13

    .set tmp, 15
    # Store value of CTR, for conditional branch sv.bc, and for VL
    .set ctr, 16

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

    .globl __vperm
    .type   __vperm, @function
__vperm:
.LFB6:
    .cfi_startproc

    # Steps required for vperm
    # 1. Compare first 8 bytes for vec3 with mask0 (0x0000_0000_0000_0000).
    #    This will generate a mask in the form 0xFF00_FFFF_0000_FF00 (example).
    # 2. AND generated mask with vec1 and store result. This corresponds to
    #    loading vec1 elements based on vec3 index.
    # 3. Compare the first 8 bytes for vec3 with mask1 (0x0101_0101_0101_0101).
    # 4. AND generated mask with vec2 and store result in a temporary.
    # 5. OR the current result with temporary to get the first half of
    #    final result
    # 6  Repeat for next value of srcstep/dststep (since we have 2 8-byte chunks).

    li                  mask0, 0
    # Load the character 0x01 into all bytes of register mask1: GPR#10
    ori                 mask1, mask1, 1
    ldbi                mask1, tmp

.setup:
    # set up ctr to 4 64-bit elements (32 bytes)
    li                  ctr, 2
    mtctr               ctr
    setvl               0, ctr, 2, 1, 1, 1      # Set VL to 4 elements, VF=1
.main_loop:
    sv.cmpb             *maskOut, *vec3, mask0
    sv.and              *res, *vec1, *maskOut
    sv.cmpb             *maskOut, *vec3, mask1
    sv.and              *tmp, *vec2, *maskOut
    sv.or               *res, *res, *tmp
    svstep.             ctr, 1, 0
    # PowerISA Book I, Section 2.4, Figure 40 BO fields
    # Branch if CTR!=0
    bdnz                .main_loop

.tail:
    blr
    .long 0
    .byte 0,0,0,0,0,0,0,0
    .cfi_endproc
.LFE6:
    .size   __vperm,.-__vperm
    .weak   vperm
    .hidden vperm
    .set    vperm,__vperm
    .ident  "GCC: (Debian 8.3.0-2) 8.3.0"
    .section    .note.GNU-stack,"",@progbits
