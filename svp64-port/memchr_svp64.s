	.file	"memchr_real.c"
	.abiversion 2
	.section	".text"
	.align 2
	.globl __memchr_svp64_real
	.type	__memchr_svp64_real, @function
__memchr_svp64_real:
.LFB6:
	.cfi_startproc
	addi 9,5,1
	rlwinm 4,4,0,0xff
	mtctr 9
.L2:
	bdnz .L4
	li 3,0
	blr
.L4:
	lbz 9,0(3)
	addi 10,3,1
	cmpw 7,9,4
	beqlr 7
	mr 3,10
	b .L2
	.long 0
	.byte 0,0,0,0,0,0,0,0
	.cfi_endproc
.LFE6:
	.size	__memchr_svp64_real,.-__memchr_svp64_real
	.weak	memchr_svp64_real
	.set	memchr_svp64_real,__memchr_svp64_real
	.ident	"GCC: (Debian 8.3.0-2) 8.3.0"
	.section	.note.GNU-stack,"",@progbits
