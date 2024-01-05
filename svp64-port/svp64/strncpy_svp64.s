# SPDX-License-Identifier: LGPL-3-or-later
# Copyright 2023 VectorCamp
# Copyright 2023 VanTosh
# Copyright 2023 Libre-SOC
#
# Funded by NGI Search Programme HORIZON-CL4-2021-HUMAN-01 2022,
# https://www.ngisearch.eu/, EU Programme 101069364.

	.machine libresoc
	.file	"strncpy.c"
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

.macro	ldbi rD, rT
	rldicr	\rT,\rD,8,55
	or		\rT,\rT,\rD
	rldicr	\rD,\rT,16,47
	or		\rD,\rD,\rT
	rldicr	\rT,\rD,32,31
	or		\rD,\rT,\rD
.endm

	.globl __strncpy
	.type	__strncpy, @function
__strncpy:
.LFB6:
	.cfi_startproc

	ori					c64, c, 0
	ldbi				c64, tmp

.outer:
	cmpldi				n, 0
	beq					.tail

	cmpldi				n, 32
	blt					.found

	li					ctr, 4
	mtctr				ctr
	setvl				0, ctr, 4, 1, 1, 1

.inner:
	sv.ld				*s, 0(in_ptr)
	sv.lbzu				*t, *s, c64
	sv.cmpi				*cr0, 1, *t, 0
	sv.bc				0, *2, -0x1c
	svstep.				ctr, 1, 0
	sv.stbu				*t, 0, 1(16)
	bdnz				.inner

	b					.outer

.found:
	mtctr				n

.found2:
	lbz					s, 0(in_ptr)
	cmpw				cr0, c, s
	beqlr				cr0
	addi				in_ptr, in_ptr, 1
	bdnz				.found

.tail:
	li					res, 0
	blr
	.long 0
	.byte 0,0,0,0,0,0,0,0
	.cfi_endproc
.LFE6:
	.size	__strncpy,.-__strncpy
	.weak	strncpy
	.hidden strncpy
	.set	strncpy,__strncpy
	.ident	"GCC: (Debian 8.3.0-2) 8.3.0"
	.section	.note.GNU-stack,"",@progbits
