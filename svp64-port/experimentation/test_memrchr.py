# Can be run standalone with:
# SILENCELOG='!instr_in_outs' python3 test_memchr.py

import unittest
from copy import deepcopy

from nmutil.formaltest import FHDLTestCase
from openpower.decoder.helpers import fp64toselectable
from openpower.decoder.isa.caller import SVP64State
from openpower.decoder.isa.test_caller import run_tst
from openpower.decoder.selectable_int import SelectableInt
from openpower.simulator.program import Program
from openpower.insndb.asm import SVP64Asm
from openpower.test.util import assemble

def ref_memrchr(s, c, n):
    res = 0
    for i in range(n-1, -1, -1):
        if s[i] == c:
            res = i
            break
    return res

def write_byte(mem, addr, val):
    addr, offs = (addr // 8)*8, (addr % 8)*8
    mask = (0xff << offs)
    value = mem.get(addr, 0) & ~mask
    value = value | (val << offs)
    mem[addr] = value & 0xffff_ffff_ffff_ffff


class DecoderTestCase(FHDLTestCase):

    def test_memrchr(self):
        """
        https://linux.die.net/man/3/memrchr
        void *memrchr(const void *s, int c, size_t n);

        The memrchr() function is like the memchr() function, except that it
        searches backward from the end of the n bytes pointed to by s instead
        of forward from the beginning. 

        This memrchr implementation uses post-increment load,
        vectorised branch conditional (sv.bc),
        and data-dependent fail first.
        Byte arrays are processed 4-bytes at a time (VL=4), and if a match
        occurs, the current pointer needs to be adjusted to account for this.
        """

        tst_string = "Hello world!\n\x00"
        #tst_string = ""
        c = 'o'
        c_ascii = ord(c) # Char to search for
        n = len(tst_string)

        start_address = 16

        expected_index = 0
        index = tst_string.find(c)
        if (n != 0) and (index != -1):
            expected_index = start_address + index

        initial_regs = [0] * 32
        # load address - will be overwritten with final pointer
        # (or null or no match)
        initial_regs[3] = start_address
        # byte to search for
        initial_regs[4] = c_ascii
        # Total number of bytes to search
        initial_regs[5] = n
        initial_regs[6] = 0 # temporary

        # some memory with identifying garbage in it
        initial_mem = {16: 0xf0f1_f2f3_f4f5_f6f7,
                       24: 0x4041_4243_4445_4647,
                       40: 0x8081_8283_8485_8687,
                       48: 0x9091_9293_9495_9697,
                       }

        for i, char in enumerate(tst_string):
            write_byte(initial_mem, 16+i, ord(char))

        # Search string four bytes at a time
        # Registers 16,17,18,19 used as temporaries
        maxvl = 4
        lst = SVP64Asm(
            [
                "cmpi 0,1,5,0", # Check if n==0
                "bc 12, 2, 0x44", # Jump to no match

                "mtspr 9, 5",                   # move r5 to CTR
                "add 7,3,5",         # start address+len
                "addi 7,7,-1", # Now points to last address of array s
                # VL (and r1) = MIN(CTR,MAXVL)
                "setvl 1,0,%d,0,1,1" % maxvl,
                # load VL bytes (update r3 addr, current pointer)
                "sv.lbzu/pi *16, -1(7)",
                # cmp against zero, truncate VL
                "sv.cmp/ff=eq/vli *0,1,*16,4",
                # test CTR, stop if any cmp failed
                "sv.bc/all 0, *2, -0x10",

                # Check for no match, add offset to get actual found address
                # If pointer just outside of array, no match.
                "cmp 0,1,3,7",
                "bc 12, 2, 0x14",

                # Adjust pointer in Reg7 because search ends at multiples of
                # VL value
                "setvl 6,0,1,0,0,0", # Get current value of VL
                "addi 6,6,%d" % ((-1*maxvl)-1), # calculate offset for found char
                # Reg 3 will now be found address, or one byte outside of array
                "add 3,7,6",
                "b 0x8",

                # No match, return null for matched address
                "addi 3,0,0",
                # this could be replaced by return call
                "nop",
            ]
        )
        lst = list(lst)

        # Produce an assembled binary
        # assembled_prog will have an attribute 'binfile' of type io.BytesIO
        # by calling 'binfile' (io.BytesIO's) 'getbuffer()' can store the binary
        # in a separate file.
        assembled_prog = assemble(lst, start_pc=0, bigendian=False)
        with open('test.bin', 'wb') as f:
            f.write(assembled_prog.binfile.getbuffer())

        with Program(lst, bigendian=False) as program:
            sim = self.run_tst_program(program, initial_mem=initial_mem,
                                       initial_regs=initial_regs)
            #mem = sim.mem.dump(printout=True, asciidump=True)
            #print (mem)
            #print(sim.gpr)
            print("Expected: %d, memrchr returned: %d" %
                  (SelectableInt(expected_index, 64), sim.gpr(3)))

            #self.assertEqual(sim.gpr(3), SelectableInt(expected_index, 64))
            print(lst)

    def run_tst_program(self, prog, initial_regs=None,
                        svstate=None, initial_fprs=None,
                        initial_mem=None):
        if initial_regs is None:
            initial_regs = [0] * 32
        if initial_fprs is None:
            initial_fprs = [0] * 32
        simulator = run_tst(prog, initial_regs, svstate=svstate,
                            initial_fprs=initial_fprs,
                            mem=initial_mem)
        print("GPRs")
        simulator.gpr.dump()
        print("FPRs")
        simulator.fpr.dump()
        return simulator


if __name__ == "__main__":
    unittest.main()
