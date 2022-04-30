// Stolen from PSL1GHT

#include "config.h"
#include <ppc-asm.h>

#define GP_ARG_MIN_REG 3
#define GP_ARG_MAX_REG 10
#define GP_ARG_NUM_REG (GP_ARG_MAX_REG - GP_ARG_MIN_REG + 1)

	.align 2
	.section ".rodata.sceFNID","a"
	.globl LIBRARY_SYMBOL
LIBRARY_SYMBOL:

#define EXPORT(name,fnid)				\
	.align 2;							\
	.section ".sceStub.text","ax";		\
	.globl __##name;					\
__##name:								\
	mflr	r0;							\
	std		r0,16(r1);					\
	std		r2,40(r1);					\
	stdu	r1,-128(r1);				\
	lis		r12,name##_stub@ha;			\
	lwz		r12,name##_stub@l(r12);		\
	lwz		r0,0(r12);					\
	lwz		r2,4(r12);					\
	mtctr	r0;							\
	bctrl;								\
	addi	r1,r1,128;					\
	ld		r2,40(r1);					\
	ld		r0,16(r1);					\
	mtlr	r0;							\
	blr;								\
	.align 3;							\
	.section ".opd","aw";				\
	.globl name;						\
name:									\
	.quad __##name,.TOC.@tocbase,0

#define EXPORT_VA(name,fnid,argc)			\
	.align 2;								\
	.section ".sceStub.text","ax";			\
	.globl __##name;						\
__##name:									\
	mflr	r0;								\
	std		r0,16(r1);						\
	std		r2,40(r1);						\
	std		r30,-16(r1);					\
	std		r31,-8(r1);						\
	stdu	r1,-160(r1);					\
	li		r12,(argc - GP_ARG_NUM_REG); 	\
	extsh.	r12,r12;						\
	ble		1f;								\
	li		r31,276;						\
	li		r30,112;						\
	mtctr	r12;							\
2:											\
	lwzx	r12,r31,r1;						\
	clrldi	r12,r12,32;						\
	stdx	r12,r30,r1;						\
	addi	r31,r31,8;						\
	addi	r30,r30,8;						\
	bdnz	2b;								\
1:											\
	lis		r12,name##_stub@ha;				\
	lwz		r12,name##_stub@l(r12);			\
	lwz		r0,0(r12);						\
	lwz		r2,4(r12);						\
	mtctr	r0;								\
	bctrl;									\
	addi	r1,r1,160;						\
	ld		r30,-16(r1);					\
	ld		r31,-8(r1);						\
	ld		r2,40(r1);						\
	ld		r0,16(r1);						\
	mtlr	r0;								\
	blr;									\
	.align 3;								\
	.section ".opd","aw";					\
	.globl name;							\
name:										\
	.quad __##name,.TOC.@tocbase,0

#include "exports.h"