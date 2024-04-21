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

# Operates on 32*8 (256-bit) value
def ref_movemask_epi8(s1):
    res = 0 # 32-bit value
    for i in range(32): # setvl VL=32
        t1 = s1[i] & 0x80
        if t1 == 0x80:
            t2 = 1<<i
            res |= t2

    return res

class DecoderTestCase(FHDLTestCase):

    def test_vpermd(self):
        """
        this function imitates the functionality of PowerISA's 'vperm' op
        """

        s1_array = [66, 164, 252, 116, 3, 248, 112, 83, 71, 155, 3, 74, 219,
                    177, 76, 24, 103, 33, 117, 116, 37, 46, 165, 47, 196, 41,
                    146, 253, 45, 147, 189, 94]
        expected = ref_movemask_epi8(s1_array)


        vec_s1_start = 2
        vecResult_start = 8

        temp1_start = 12
        temp2_start = 14
        temp3_start = 16

        mask = 20
        shiftR_cnt = 21
        shiftL_cnt = 22
        const_1 = 23
        vl_count = 24
        zero = 25

        initial_regs = [0] * 32

        # Temporaries
        initial_regs[temp1_start]   = 0
        initial_regs[temp1_start+1] = 0
        initial_regs[temp1_start+2] = 0
        initial_regs[temp1_start+3] = 0

        initial_regs[temp2_start]   = 0
        initial_regs[temp3_start]   = 0
        initial_regs[shiftR_cnt]   = 0
        initial_regs[shiftL_cnt]   = 0
        initial_regs[const_1]   = 1
        initial_regs[vl_count]   = 4
        initial_regs[zero]   = 0
        #initial_regs[mask]   = 0x8080808080808080

        # Input vectors 1
        initial_regs[vec_s1_start]   = 0x42a4fc7403f87083
        initial_regs[vec_s1_start+1] = 0x479b034adbb14c18
        initial_regs[vec_s1_start+2] = 0x67217574252ea52f
        initial_regs[vec_s1_start+3] = 0xc42992fd2d93bd5e

        maxvl = 2
        program_text = \
            [
            "setvl 1, 0, 4, 1, 1, 1",
            # .svstep_loop:
            "addi %d, 0, 0" % (shiftR_cnt), # clear shift amount
            "mtspr 9, 8",
            # .inner_loop:
            # SVP64Asm() seems to incorrectly convert vector operand for srd,
            # Using temp reg
            "sv.add *%d, *%d, %d" % (temp1_start, vec_s1_start, zero),
            "sv.srd *%d, *%d, %d" % (temp2_start, temp1_start, shiftR_cnt),
            "addi %d, %d, 8" % (shiftR_cnt, shiftR_cnt), # Increase shift value
            "sv.andi. *%d, *%d, 0x80" % (temp2_start, temp2_start),
            "sv.cmpi *cr0, 1, *%d, 0x80" % (temp2_start),
            "sv.bc 4, *2, 0x0c", # Not equal to 0x80
            # Set a result bit corresponding to input vector element's MSb
            "sv.sld *%d, %d, %d" % (temp2_start, const_1, shiftL_cnt),
            "sv.or *%d, *%d, *%d" % (vecResult_start, vecResult_start, temp2_start),
            "bc 16, 0, -0x3c",
            "svstep. 0, 1, 0",
            "addi %d, %d, -1" % (vl_count, vl_count),
            "cmpi cr0, 1, %d, 0" % (vl_count),
            "bc 4, 2, -0x50",
            # this could be replaced by return call
            "nop",
            ]
        
        lst = SVP64Asm(program_text)
        lst = list(lst)
        print(lst)
        #exit()

        # Produce an assembled binary
        # assembled_prog will have an attribute 'binfile' of type io.BytesIO
        # by calling 'binfile' (io.BytesIO's) 'getbuffer()' can store the binary
        # in a separate file.
        assembled_prog = assemble(lst, start_pc=0, bigendian=False)
        with open('test.bin', 'wb') as f:
            f.write(assembled_prog.binfile.getbuffer())

        with Program(lst, bigendian=False) as program:
            sim = self.run_tst_program(program,
                                       initial_regs=initial_regs)
            #mem = sim.mem.dump(printout=True, asciidump=True)
            #print (mem)
            print(sim.gpr)
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
