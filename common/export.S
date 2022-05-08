// Stolen from PSL1GHT

#include <config.h>

#define GP_ARG_MIN_REG 3
#define GP_ARG_MAX_REG 10
#define GP_ARG_NUM_REG (GP_ARG_MAX_REG - GP_ARG_MIN_REG + 1)

	.align 2
	.section ".rodata.sceFNID","a"
	.globl LIBRARY_SYMBOL
LIBRARY_SYMBOL:

#define EXPORT(name,fnid)				    \
	.align 2;							    \
	.section ".sceStub.text","ax";		    \
	.globl __##name;					    \
__##name:								    \
	mflr	0;							    \
	std		0,16(1);					    \
	std		2,40(1);					    \
	stdu	1,-128(1);				        \
	lis		12,name##_stub@ha;			    \
	lwz		12,name##_stub@l(12);		    \
	lwz		0,0(12);					    \
	lwz		2,4(12);					    \
	mtctr	0;							    \
	bctrl;								    \
	addi	1,1,128;					    \
	ld		2,40(1);					    \
	ld		0,16(1);					    \
	mtlr	0;							    \
	blr;								    \
	.align 3;							    \
	.section ".opd","aw";				    \
	.globl name;						    \
name:									    \
	.quad __##name,.TOC.@tocbase,0

#define EXPORT_VA(name,fnid,argc)			\
	.align 2;								\
	.section ".sceStub.text","ax";			\
	.globl __##name;						\
__##name:									\
	mflr	0;								\
	std		0,16(1);						\
	std		2,40(1);						\
	std		30,-16(1);					    \
	std		31,-8(1);						\
	stdu	1,-160(1);					    \
	li		12,(argc - GP_ARG_NUM_REG); 	\
	extsh.	12,12;						    \
	ble		1f;								\
	li		31,276;						    \
	li		30,112;						    \
	mtctr	12;							    \
2:											\
	lwzx	12,31,1;						\
	clrldi	12,12,32;						\
	stdx	12,30,1;						\
	addi	31,31,8;						\
	addi	30,30,8;						\
	bdnz	2b;								\
1:											\
	lis		12,name##_stub@ha;				\
	lwz		12,name##_stub@l(r12);			\
	lwz		0,0(12);						\
	lwz		2,4(12);						\
	mtctr	0;								\
	bctrl;									\
	addi	1,1,160;						\
	ld		30,-16(1);					    \
	ld		31,-8(1);						\
	ld		2,40(1);						\
	ld		0,16(1);						\
	mtlr	0;								\
	blr;									\
	.align 3;								\
	.section ".opd","aw";					\
	.globl name;							\
name:										\
	.quad __##name,.TOC.@tocbase,0

#include "exports.h"