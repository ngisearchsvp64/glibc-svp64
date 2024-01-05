# SPDX-License-Identifier: LGPL-3-or-later
# Copyright 2023 VectorCamp
# Copyright 2023 Red Semiconductor Ltd.
# Copyright 2023 Vantosh
#
# Funded by NGI Search Programme HORIZON-CL4-2021-HUMAN-01 2022,
# https://www.ngisearch.eu/, EU Programme 101069364.

# A simple Makefile, to build run: make all
memchr_TARGET	= test-memchr-svp64
memrchr_TARGET	= test-memrchr-svp64
strchr_TARGET	= test-strchr-svp64
strcat_TARGET	= test-strcat-svp64
strcmp_TARGET	= test-strcmp-svp64
strncpy_TARGET	= test-strncpy-svp64

AS = powerpc64le-linux-gnu-as
CC = gcc
LD = ld
CROSSCC = powerpc64le-linux-gnu-gcc-8
CROSSOBJCOPY = powerpc64le-linux-gnu-objcopy
CROSSLD = powerpc64le-linux-gnu-ld

GLIBCBUILD = ../build
GLIBCDIR = ../glibc
SVP64 = svp64

GLIBCFLAGS = -std=gnu11 -fgnu89-inline -Wall -Wundef -Wwrite-strings -fmerge-all-constants -fno-stack-protector -frounding-math -g -Wstrict-prototypes -Wold-style-definition -fmath-errno
GLIBCFLAGS += -I$(GLIBCDIR)/include -I$(GLIBCBUILD)/string  -I$(GLIBCBUILD)/build \
              -I$(GLIBCDIR)/sysdeps/unix/sysv/linux/x86_64/64  -I$(GLIBCDIR)/sysdeps/unix/sysv/linux/x86_64 \
              -I$(GLIBCDIR)/sysdeps/unix/sysv/linux/x86/include -I$(GLIBCDIR)/sysdeps/unix/sysv/linux/x86 \
              -I$(GLIBCDIR)/sysdeps/x86/nptl  -I$(GLIBCDIR)/sysdeps/unix/sysv/linux/wordsize-64  -I$(GLIBCDIR)/sysdeps/x86_64/nptl \
              -I$(GLIBCDIR)/sysdeps/unix/sysv/linux/include -I$(GLIBCDIR)/sysdeps/unix/sysv/linux  -I$(GLIBCDIR)/sysdeps/nptl  \
              -I$(GLIBCDIR)/sysdeps/pthread  -I$(GLIBCDIR)/sysdeps/gnu  -I$(GLIBCDIR)/sysdeps/unix/inet  -I$(GLIBCDIR)/sysdeps/unix/sysv \
              -I$(GLIBCDIR)/sysdeps/unix/x86_64  -I$(GLIBCDIR)/sysdeps/unix  -I$(GLIBCDIR)/sysdeps/posix  -I$(GLIBCDIR)/sysdeps/x86_64/64 \
              -I$(GLIBCDIR)/sysdeps/x86_64/fpu  -I$(GLIBCDIR)/sysdeps/x86/fpu/include -I$(GLIBCDIR)/sysdeps/x86/fpu  -I$(GLIBCDIR)/sysdeps/x86_64 \
              -I$(GLIBCDIR)/sysdeps/x86  -I$(GLIBCDIR)/sysdeps/ieee754/float128  -I$(GLIBCDIR)/sysdeps/ieee754/ldbl-96/include \
              -I$(GLIBCDIR)/sysdeps/ieee754/ldbl-96  -I$(GLIBCDIR)/sysdeps/ieee754/dbl-64/wordsize-64  -I$(GLIBCDIR)/sysdeps/ieee754/dbl-64 \
              -I$(GLIBCDIR)/sysdeps/ieee754/flt-32  -I$(GLIBCDIR)/sysdeps/wordsize-64  -I$(GLIBCDIR)/sysdeps/ieee754  -I$(GLIBCDIR)/sysdeps/generic \
              -I$(GLIBCDIR)/string \
              -I$(GLIBCDIR) -I$(GLIBCDIR)/libio -I../build
GLIBCFLAGS += -D_LIBC_REENTRANT -include $(GLIBCBUILD)/libc-modules.h -include $(GLIBCDIR)/include/libc-symbols.h  -DPIC -DTOP_NAMESPACE=glibc

#TESTERLDFLAGS = -pie -Wl,-O1 -nostdlib -nostartfiles -Wl,-z,combreloc -Wl,-z,relro -Wl,--hash-style=both $(GLIBCBUILD)/csu/Scrt1.o $(GLIBCBUILD)/csu/crti.o \
                `gcc  --print-file-name=crtbeginS.o` $(GLIBCBUILD)/string/tester.o $(GLIBCBUILD)/support/libsupport_nonshared.a \
                -Wl,-dynamic-linker=/usr/local/lib/ld-linux-x86-64.so.2 -Wl,-rpath-link=$(GLIBCBUILD):$(GLIBCBUILD)/math:$(GLIBCBUILD)/elf:$(GLIBCBUILD)/dlfcn:$(GLIBCBUILD)/nss:$(GLIBCBUILD)/nis:$(GLIBCBUILD)/rt:$(GLIBCBUILD)/resolv:$(GLIBCBUILD)/mathvec:$(GLIBCBUILD)/support:$(GLIBCBUILD)/nptl \
                $(GLIBCBUILD)/libc.so.6 $(GLIBCBUILD)/libc_nonshared.a -Wl,--as-needed $(GLIBCBUILD)/elf/ld.so -Wl,--no-as-needed -lgcc \
                -Wl,--as-needed -lgcc_s  -Wl,--no-as-needed `gcc  --print-file-name=crtendS.o` $(GLIBCBUILD)/csu/crtn.o

#compiler flags here
CROSSCFLAGS = $(GLIBCFLAGS) -g3 -Os -Wall -Wextra
CFLAGS = $(GLIBCFLAGS) -g3 -Os -Wall -Wextra -I../openpower-isa/media/pypowersim_wrapper -I/usr/include/python3.7m #-fsanitize=address

# assembler flags here
ASFLAGS= -mlibresoc -mregnames -Isrc 

#linker flags here
LDFLAGS = -Wall -pthread -lpython3.7m #-lasan

BINDIR  = bin

memchr_CFILES	:= support_test_main.c test-memchr.c memchr_wrapper.c
memchr_ASFILES := $(SVP64)/memchr_svp64.s $(SVP64)/memchr_orig_ppc64.s
memchr_SVP64OBJECTS := $(memchr_ASFILES:$(SVP64)/%.s=$(SVP64)/%.o)
memchr_OBJECTS := $(memchr_CFILES:%.c=%.o)
memchr_BINFILES := $(BINDIR)/memchr_svp64.bin
memchr_ELFFILES := $(BINDIR)/memchr_svp64.elf

memrchr_CFILES	:= support_test_main.c test-memrchr.c memrchr_wrapper.c
memrchr_ASFILES := $(SVP64)/memrchr_svp64.s
memrchr_SVP64OBJECTS := $(memrchr_ASFILES:$(SVP64)/%.s=$(SVP64)/%.o)
memrchr_OBJECTS := $(memrchr_CFILES:%.c=%.o)
memrchr_BINFILES := $(BINDIR)/memrchr_svp64.bin
memrchr_ELFFILES := $(BINDIR)/memrchr_svp64.elf

strchr_CFILES	:= support_test_main.c test-strchr.c strchr_wrapper.c
strchr_ASFILES := $(SVP64)/strchr_svp64.s $(SVP64)/strchr_orig_ppc64.s
strchr_SVP64OBJECTS := $(strchr_ASFILES:$(SVP64)/%.s=$(SVP64)/%.o)
strchr_OBJECTS := $(strchr_CFILES:%.c=%.o)
strchr_BINFILES := $(BINDIR)/strchr_svp64.bin
strchr_ELFFILES := $(BINDIR)/strchr_svp64.elf

strcat_CFILES	:= support_test_main.c test-strcat.c strcat_wrapper.c
strcat_ASFILES := $(SVP64)/strcat_svp64.s $(SVP64)/strcat_orig_ppc64.s
strcat_SVP64OBJECTS := $(strcat_ASFILES:$(SVP64)/%.s=$(SVP64)/%.o)
strcat_OBJECTS := $(strchr_CFILES:%.c=%.o)
strcat_BINFILES := $(BINDIR)/strcat_svp64.bin
strcat_ELFFILES := $(BINDIR)/strcat_svp64.elf

strcmp_CFILES	:= support_test_main.c test-strcmp.c strcmp_wrapper.c
strcmp_ASFILES := $(SVP64)/strcmp_svp64.s $(SVP64)/strcmp_orig_ppc64.s
strcmp_SVP64OBJECTS := $(strcmp_ASFILES:$(SVP64)/%.s=$(SVP64)/%.o)
strcmp_OBJECTS := $(strchr_CFILES:%.c=%.o)
strcmp_BINFILES := $(BINDIR)/strcmp_svp64.bin
strcmp_ELFFILES := $(BINDIR)/strcmp_svp64.elf

strncpy_CFILES	:= support_test_main.c test-strncpy.c strncpy_wrapper.c
strncpy_ASFILES := $(SVP64)/strncpy_svp64.s $(SVP64)/strncpy_orig_ppc64.s
strncpy_SVP64OBJECTS := $(strncpy_ASFILES:$(SVP64)/%.s=$(SVP64)/%.o)
strncpy_OBJECTS := $(strncpy_CFILES:%.c=%.o)
strncpy_BINFILES := $(BINDIR)/strncpy_svp64.bin
strncpy_ELFFILES := $(BINDIR)/strncpy_svp64.elf

test-memchr.o: test-memchr.c
	$(CC) -c $(CFLAGS) -DMODULE_NAME=testsuite -o $@ $^

test-memrchr.o: test-memrchr.c
	$(CC) -c $(CFLAGS) -DMODULE_NAME=testsuite -o $@ $^

test-strchr.o: test-strchr.c
	$(CC) -c $(CFLAGS) -DMODULE_NAME=testsuite -o $@ $^

test-strcat.o: test-strcat.c
	$(CC) -c $(CFLAGS) -DMODULE_NAME=testsuite -o $@ $^

test-strcmp.o: test-strcmp.c
	$(CC) -c $(CFLAGS) -DMODULE_NAME=testsuite -o $@ $^

test-strncpy.o: test-strncpy.c
	$(CC) -c $(CFLAGS) -DMODULE_NAME=testsuite -o $@ $^

$(SVP64)/memchr_orig_ppc64.s: $(GLIBCDIR)/string/memchr.c
	$(CROSSCC) $(CROSSCFLAGS) -S -g0 -Os -DMODULE_NAME=libc -o $@ $^

$(SVP64)/strchr_orig_ppc64.s: $(GLIBCDIR)/string/strchr.c
	$(CROSSCC) $(CROSSCFLAGS) -S -g0 -Os -DMODULE_NAME=libc -o $@ $^

$(SVP64)/strcat_orig_ppc64.s: $(GLIBCDIR)/string/strcat.c
	$(CROSSCC) $(CROSSCFLAGS) -S -g0 -Os -DMODULE_NAME=libc -o $@ $^

$(SVP64)/strcmp_orig_ppc64.s: $(GLIBCDIR)/string/strcmp.c
	$(CROSSCC) $(CROSSCFLAGS) -S -g0 -Os -DMODULE_NAME=libc -o $@ $^

$(SVP64)/strncpy_orig_ppc64.s: $(GLIBCDIR)/string/strncpy.c
	$(CROSSCC) $(CROSSCFLAGS) -S -g0 -Os -DMODULE_NAME=libc -o $@ $^

$(BINDIR)/%.elf: $(SVP64)/%.o
	$(CROSSLD) -EL -o $@ -T memmap $^

$(BINDIR)/%.bin: $(BINDIR)/%.elf
	$(CROSSOBJCOPY) -I elf64-little -O binary $< $@

.PHONY: all clean remove
all: $(BINDIR) $(memchr_TARGET) $(memrchr_TARGET) $(strchr_TARGET) $(strcat_TARGET) $(strcmp_TARGET) $(strncpy_TARGET)

$(BINDIR):
	mkdir -p $(BINDIR)

$(memchr_TARGET): $(memchr_OBJECTS) $(memchr_SVP64OBJECTS) $(memchr_ELFFILES) $(memchr_BINFILES)
	$(CC) -o $@ $(memchr_OBJECTS) $(LDFLAGS)

$(memrchr_TARGET): $(memrchr_OBJECTS) $(memrchr_SVP64OBJECTS) $(memrchr_ELFFILES) $(memrchr_BINFILES)
	$(CC) -o $@ $(memrchr_OBJECTS) $(LDFLAGS)

$(strchr_TARGET): $(strchr_OBJECTS) $(strchr_SVP64OBJECTS) $(strchr_ELFFILES) $(strchr_BINFILES)
	$(CC) -o $@ $(strchr_OBJECTS) $(LDFLAGS)

$(strcat_TARGET): $(strcat_OBJECTS) $(strcat_SVP64OBJECTS) $(strcat_ELFFILES) $(strcat_BINFILES)
	$(CC) -o $@ $(strcat_OBJECTS) $(LDFLAGS)

$(strcmp_TARGET): $(strcmp_OBJECTS) $(strcmp_SVP64OBJECTS) $(strcmp_ELFFILES) $(strcmp_BINFILES)
	$(CC) -o $@ $(strcmp_OBJECTS) $(LDFLAGS)

$(strncpy_TARGET): $(strncpy_OBJECTS) $(strncpy_SVP64OBJECTS) $(strncpy_ELFFILES) $(strncpy_BINFILES)
	$(CC) -o $@ $(strncpy_OBJECTS) $(LDFLAGS)

clean:
	$ rm -f $(memchr_OBJECTS) $(memchr_SVP64OBJECTS) $(memchr_BINFILES) $(memchr_ELFFILES) $(memchr_TARGET)
	$ rm -f $(memrchr_OBJECTS) $(memrchr_SVP64OBJECTS) $(memrchr_BINFILES) $(memrchr_ELFFILES) $(memrchr_TARGET)
	$ rm -f $(strcat_OBJECTS) $(strcat_SVP64OBJECTS) $(strcat_BINFILES) $(strcat_ELFFILES) $(strcat_TARGET)
	$ rm -f $(strcmp_OBJECTS) $(strcmp_SVP64OBJECTS) $(strcmp_BINFILES) $(strcmp_ELFFILES) $(strcmp_TARGET)
	$ rm -f $(strncpy_OBJECTS) $(strncpy_SVP64OBJECTS) $(strncpy_BINFILES) $(strncpy_ELFFILES) $(strncpy_TARGET)

remove: clean
	$ rm -f $(memchr_TARGET) $(memrchr_TARGET) $(strchr_TARGET) $(strcat_TARGET) $(strcmp_TARGET) $(strncpy_TARGET)
