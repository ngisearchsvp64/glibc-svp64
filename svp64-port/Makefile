# A simple Makefile, to build run: make all
TARGET	= test-memchr-svp64

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
CFLAGS = $(GLIBCFLAGS) -g3 -Os -Wall -Wextra -I../openpower-isa/media/pypowersim_wrapper -I/usr/include/python3.7m -fsanitize=address

# assembler flags here
ASFLAGS= -mlibresoc -mregnames -Isrc 

#linker flags here
LDFLAGS = -Wall -pthread -lasan -lpython3.7m

BINDIR  = bin

CFILES	:= support_test_main.c test-memchr.c memchr_wrapper.c
ASFILES := $(SVP64)/memchr_svp64.s
SVP64OBJECTS := $(ASFILES:%.s=%.o)
OBJECTS := $(CFILES:%.c=%.o)
BINFILES := $(BINDIR)/memchr_svp64.bin
ELFFILES := $(BINDIR)/memchr_svp64.elf

test-memchr.o: test-memchr.c
	$(CC) -c $(CFLAGS) -DMODULE_NAME=testsuite -o $@ $^

$(SVP64)/memchr_svp64.s: $(GLIBCDIR)/string/memchr.c
	$(CROSSCC) $(CROSSCFLAGS) -S -g0 -Os -DMODULE_NAME=libc -o $@ $^

$(BINDIR)/%.elf: $(SVP64)/%.o
	$(CROSSLD) -EL -o $@ -T memmap $^

$(BINDIR)/%.bin: $(BINDIR)/%.elf
	$(CROSSOBJCOPY) -I elf64-little -O binary $< $@

.PHONY: all clean remove
all: $(BINDIR) $(TARGET)

$(BINDIR):
	mkdir -p $(BINDIR)

$(TARGET): $(OBJECTS) $(SVP64OBJECTS) $(ELFFILES) $(BINFILES)
	$(CC) -o $@ $(OBJECTS) $(LDFLAGS)

clean:
	$ rm -f $(OBJECTS) $(SVP64OBJECTS) $(BINFILES) $(ELFFILES) $(TARGET) $(SVP64)/memchr_svp64.s

remove: clean
	$ rm -f $(TARGET)
