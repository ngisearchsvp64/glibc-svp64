	.file	"memchr.c"
	.abiversion 2
	.section	".text"
	.align 2
	.globl __memchr
	.type	__memchr, @function
__memchr:
.LFB6:
	.cfi_startproc
	addi 9,5,1
	rlwinm 8,4,0,0xff
	mtctr 9
.L2:
	bdz .L4
	andi. 9,3,0x7
	bne 0,.L5
.L4:
	rlwinm 9,4,8,16,23
	rlwinm 4,4,0,24,31
	or 4,9,4
	lis 7,0xfefe
	extsw 4,4
	lis 6,0x8080
	sldi 9,4,16
	ori 7,7,0xfefe
	or 4,9,4
	ori 6,6,0x8080
	sldi 9,4,32
	sldi 7,7,32
	or 4,9,4
	srdi 9,5,3
	addi 9,9,1
	sldi 6,6,32
	mtctr 9
	oris 7,7,0xfefe
	oris 6,6,0x8080
	ori 7,7,0xfeff
	ori 6,6,0x8080
.L6:
	bdnz .L8
.L7:
	addi 9,5,1
	mtctr 9
	b .L9
.L5:
	lbz 9,0(3)
	cmpw 7,9,8
	beqlr 7
	addi 5,5,-1
	addi 3,3,1
	b .L2
.L8:
	ld 9,0(3)
	xor 10,4,9
	add 9,10,7
	andc 9,9,10
	and. 9,9,6
	bne 0,.L7
	addi 3,3,8
	addi 5,5,-8
	b .L6
.L10:
	lbz 9,0(3)
	cmpw 7,9,8
	beqlr 7
	addi 3,3,1
.L9:
	bdnz .L10
	li 3,0
	blr
	.long 0
	.byte 0,0,0,0,0,0,0,0
	.cfi_endproc
.LFE6:
	.size	__memchr,.-__memchr
	.weak	memchr
	.hidden	memchr
	.set	memchr,__memchr
	.ident	"GCC: (Debian 8.3.0-2) 8.3.0"
	.section	.note.GNU-stack,"",@progbits
