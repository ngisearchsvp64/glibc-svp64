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

def test_ref_vpermd():
    vec1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    vec2 = [45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30]
    vec3 = [0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1]

    result = vpermd(vec1, vec2, vec3)
    print("Vec1:", vec1)
    print("Vec2:", vec2)
    print("Vec3:", vec3)
    print("Res :", result)

class DecoderTestCase(FHDLTestCase):

    def _check_regs(self, sim, expected):
        for i in range(32):
            self.assertEqual(sim.gpr(i), SelectableInt(expected[i], 64))

    def _check_fpregs(self, sim, expected):
        for i in range(32):
            self.assertEqual(sim.fpr(i), SelectableInt(expected[i], 64))

    def test_vpermd(self):
        """
        this function imitates the functionality of PowerISA's 'vperm' op
        """

        # For convenience, set a variable for where this vector will start
        # Make sure there is a gap of two between vec1, vec2, vec3, result,
        # else overlap will occur.
        # This is because 2 registers are needed to store 16 bytes.
        vec1_start = 2
        vec2_start = 4
        vec3_start = 6
        vecResult_start = 8
        maskReg_start = 10

        temp1_start = 12
        temp2_start = 14
        temp3_start = 16

        initial_regs = [0] * 32

        # Temporaries - tmp 1 stores mask for vec2
        initial_regs[temp1_start]   = 0
        initial_regs[temp1_start+1] = 0
        initial_regs[temp2_start]   = 0x0101010101010101
        initial_regs[temp2_start+1] = 0x0101010101010101
        initial_regs[temp3_start]   = 0
        initial_regs[temp3_start+1] = 0
        # Used for computing mask for vec1/vec2
        initial_regs[maskReg_start]   = 0
        initial_regs[maskReg_start+1] = 0

        # Input vectors 1 and 2
        initial_regs[vec1_start]   = 0x0102030405060708
        initial_regs[vec1_start+1] = 0x0910111213141516
        initial_regs[vec2_start]   = 0x4544434241403938
        initial_regs[vec2_start+1] = 0x3736353433323130
        # Vector 3 - used to select between vec1 and vec2
        initial_regs[vec3_start]   = 0x0001010001000101
        initial_regs[vec3_start+1] = 0x0100000001010001

        maxvl = 2
        program_text = \
            [
            "mtspr 9, 2", # element width = 64, working in 2 blocks of 8 bytes
            "setvl 1, 0, %d, 0, 1, 1" % maxvl,
            # This creates a mask
            "sv.cmpb *%d, *%d, %d" % (maskReg_start, vec3_start, temp1_start),
            "sv.and *%d, *%d, *%d" % (vecResult_start, vec1_start, maskReg_start),
            "sv.cmpb *%d, *%d, %d" % (maskReg_start, vec3_start, temp2_start),
            "sv.and *%d, *%d, *%d" % (temp3_start, vec2_start, maskReg_start),
            "sv.or *%d, *%d, *%d" % (vecResult_start, vecResult_start, temp3_start),
            "sv.bc 18,0,0x8",
            "b -0x18",
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
