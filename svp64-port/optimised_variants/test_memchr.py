import unittest
from copy import deepcopy

from nmutil.formaltest import FHDLTestCase
from openpower.decoder.helpers import fp64toselectable
from openpower.decoder.isa.caller import SVP64State
from openpower.decoder.isa.test_caller import run_tst
from openpower.decoder.selectable_int import SelectableInt
from openpower.simulator.program import Program
from openpower.insndb.asm import SVP64Asm


def write_byte(mem, addr, val):
    addr, offs = (addr // 8)*8, (addr % 8)*8
    mask = (0xff << offs)
    value = mem.get(addr, 0) & ~mask
    value = value | (val << offs)
    mem[addr] = value & 0xffff_ffff_ffff_ffff


class DecoderTestCase(FHDLTestCase):

    def _check_regs(self, sim, expected):
        for i in range(32):
            self.assertEqual(sim.gpr(i), SelectableInt(expected[i], 64))

    def _check_fpregs(self, sim, expected):
        for i in range(32):
            self.assertEqual(sim.fpr(i), SelectableInt(expected[i], 64))

    def test_memchr(self):
        """

        The memchr function locates the first occurrence of c
        (converted to an unsigned char) in the initial n characters
        (each interpreted as unsigned char) of the object pointed to by s.
        The implementation shall behave as if it reads the characters
        sequentially and stops as soon as a matching character is found.

        The memchr function returns a pointer to the located character,
        or a null pointer if the character does not occur in the object.

        strncpy using post-increment ld/st, sv.bc, and data-dependent ffirst.
        note that /lf (Load-Fault) mode is not set in this example when it
        should be. however implementing Load-Fault in ISACaller is tricky
        (requires implementing multiple hardware models)
        """

        tst_string = "Hello world!\n\x00"
        c = 'w'
        c_ascii = ord('w') # Char to search for
        n = len(tst_string)
        expected_index = tst_string.find('w')
        
        initial_regs = [0] * 32
        initial_regs[3] = n
        initial_regs[4] = 0 # Address of found character
        initial_regs[10] = 16  # load address

        # some memory with identifying garbage in it
        initial_mem = {16: 0xf0f1_f2f3_f4f5_f6f7,
                       24: 0x4041_4243_4445_4647,
                       40: 0x8081_8283_8485_8687,
                       48: 0x9091_9293_9495_9697,
                       }

        for i, char in enumerate(tst_string):
            write_byte(initial_mem, 16+i, ord(char))

        maxvl = n+1
        lst = SVP64Asm(
            [
                "mtspr 9, 3",                   # move r3 to CTR
                "addi 0,0,0",                   # initialise r0 to zero
                # chr-copy loop starts here:
                #   for (i = 0; i < n && src[i] != '\0'; i++)
                #        dest[i] = src[i];
                # VL (and r1) = MIN(CTR,MAXVL)
                "setvl 1,0,%d,0,1,1" % maxvl,
                # load VL bytes (update r10 addr)
                "sv.lbzu/pi *16, 1(10)",         # should be /lf here as well
                # TODO: For now just hard-code required char c
                "sv.cmpi/ff=eq/vli *0,1,*16,%d" % c_ascii,  # cmp against zero, truncate VL
                # store VL bytes (update r12 addr)
                #---"sv.stbu/pi *16, 1(12)",
                "svstep 0,1,1", # return current step (found char index)
                "sv.bc/all 0, *2, -0x18",       # test CTR, stop if cmpi failed
            ]
        )
        lst = list(lst)

        with Program(lst, bigendian=False) as program:
            sim = self.run_tst_program(program, initial_mem=initial_mem,
                                       initial_regs=initial_regs)
            mem = sim.mem.dump(printout=True, asciidump=True)
            print (mem)
            print(sim.gpr)
            print(expected_index)

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
