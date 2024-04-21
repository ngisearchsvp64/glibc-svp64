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

def ref_vpermd(vec1, vec2, vec3):
    vecResult = [0]*16
    for i in range(16): # setvl VL=16
        if vec3[i] == 0:
            vecResult[i] = vec1[i]
        else:
            vecResult[i] = vec2[i]

    return vecResult

# takes in two unsigned array bytes, 32 elements long
# Intel doc:
# https://www.intel.com/content/www/us/en/docs/cpp-compiler/developer-guide-reference/2021-8/mm256-shuffle-epi8.html
def ref__mm256_shuffle_epi8(a, b):
    r = [0] * 32
    for i in range(0, 16):
        # Lower half
        if b[i] & 0x80:
            r[i] = 0
        else:
            r[i] = a[b[i] & 0x0F]
        # Upper half
        if b[16+i] & 0x80:
            r[16+i] = 0
        else:
            r[16+i] = a[16+(b[16+i] & 0x0F)]

    print("Vec a :", a)
    print("Vec b :", b)
    print("Result:", r)
    return r

class DecoderTestCase(FHDLTestCase):

    def test_shuffle_epi8(self):
        """
        function imitates the function of Intel's '_mm256_shuffle_epi8' op
        """

        a = [ 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,
             17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
        b = [14|0x80, 15, 0, 2, 10, 13, 1, 5|0x80, 3|0x80, 2|0x80, 4|0x80, 1, 12, 2, 5,
             10, 5, 12, 4, 10|0x80, 14, 13, 12, 0, 14, 15, 0, 14, 8, 14, 7, 11]
        result = ref__mm256_shuffle_epi8(a, b)

        # For convenience, set a variable for where this vector will start
        # Make sure there is a gap of two between vec1, vec2, vec3, result,
        # else overlap will occur.
        # This is because 2 registers are needed to store 16 bytes.
        vec_a_start = 2
        vec_b_start = 6
        vec_r_start = 10

        vec_a_mid = vec_a_start+2
        vec_b_mid = vec_b_start+2
        vec_r_mid = vec_r_start+2

        temp1_start = 14
        temp2_start = 18
        temp3_start = 22

        initial_regs = [0] * 32

        # Temporaries - tmp 1 stores mask for vec2
        initial_regs[temp1_start]   = 0
        initial_regs[temp1_start+1] = 0
        initial_regs[temp2_start]   = 0
        initial_regs[temp2_start+1] = 0
        initial_regs[temp3_start]   = 0
        initial_regs[temp3_start+1] = 0

        # Input vectors 1 and 2
        initial_regs[vec_a_start]   = 0x0102030405060708
        initial_regs[vec_a_start+1] = 0x090a0b0c0d0e0f10
        initial_regs[vec_a_start+2] = 0x1112131415161718
        initial_regs[vec_a_start+3] = 0x191a1b1c1d1e1f20

        initial_regs[vec_b_start]   = 0x8e0f00020a0d0185
        initial_regs[vec_b_start+1] = 0x838284010c02050a
        initial_regs[vec_b_start+2] = 0x050c048a0e0d0c00
        initial_regs[vec_b_start+3] = 0x0e0f000e080e070b

        #TODO:
        program_text = \
            [
            "setvl 1, 0, 32, 0, 1, 0", # Horizontal-First mode
            # Create temp where only lower nibble of each element in b set.
            "sv.andi/ew=8 *%d, *%d, 0x0f" % (temp1_start, vec_b_start),
            "mtspr 9, 16", # 32*8-bit elements, but only working on half
            # Check if upper bit set, then clear result element if so
            "setvl 1, 0, 16, 0, 1, 1", # Vertical-First mode
            ".lower_loop:"
            "sv.andi/ew=8 *%d, %d, 0x80" % (temp2_start, vec_b_start),
            "sv.cmpi/ew=8 cr0, 1, *%d, 0x80" % (vec_b_start),
            #TODO: branch if b[i]==0x80
            "sv.bc 12, 2, .clear",
            #TODO: Choose correct SVG, enable REMAP on operand RA,
            # ew=8 (0b11), mm=0, sk=0
            "svindex %d, 0b10000, 4, 3, 0, 0" % (vec_b_start>>2),
            "sv.addi/ew=8 *%d, *%d, 0" % (vec_r_start, vec_b_start),
            "b .step",
            ".clear:",
            "sv.addi %d, 0, 0" % (vec_r_start),
            ".step:"
            "svstep. 0, 1, 0",
            "bdnz .lower_loop",
            # upper half TODO

            # this could be replaced by return call
            "nop",
            ]
        
        lst = SVP64Asm(program_text)
        lst = list(lst)
        print(lst)
        exit()

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
