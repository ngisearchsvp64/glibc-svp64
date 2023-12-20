/* Copyright (C) 1991-2018 Free Software Foundation, Inc.
   This file is part of the GNU C Library.
   Based on strlen implementation by Torbjorn Granlund (tege@sics.se),
   with help from Dan Sahlin (dan@sics.se) and
   commentary by Jim Blandy (jimb@ai.mit.edu);
   adaptation to memchr suggested by Dick Karpinski (dick@cca.ucsf.edu),
   and implemented by Roland McGrath (roland@ai.mit.edu).

   The GNU C Library is free software; you can redistribute it and/or
   modify it under the terms of the GNU Lesser General Public
   License as published by the Free Software Foundation; either
   version 2.1 of the License, or (at your option) any later version.

   The GNU C Library is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   Lesser General Public License for more details.

   You should have received a copy of the GNU Lesser General Public
   License along with the GNU C Library; if not, see
   <http://www.gnu.org/licenses/>.  */

/* Copyright 2023 VectorCamp
   Copyright 2023 Red Semiconductor Ltd.
   Funded by NGI Search Programme HORIZON-CL4-2021-HUMAN-01 2022,
   https://www.ngisearch.eu/, EU Programme 101069364. */

#ifndef _LIBC
# include <config.h>
#endif

#include <string.h>

#include <stddef.h>

#include <limits.h>

#undef __strchr_svp64
#ifdef _LIBC
# undef strchr_svp64
#endif

#ifndef weak_alias
# define __strchr_svp64 strchr_svp64
#endif

#ifndef STRCHR_SVP64
# define STRCHR_SVP64 __strchr_svp64
#endif

#include <Python.h>
#include <stdint.h>
#include <stdio.h>

#include "pypowersim_wrapper_common.h"

const char *strchr_svp64_filename = "./bin/strchr_svp64.bin";

/* Search S for C until NULL string terminator encountered.  */
char*
STRCHR_SVP64 (const char *s, int c)
{
    #define REG_s 3 // Set GPR #3 to the pointer s
    #define REG_c 4 // Set GPR #4 to the char 'c'

    printf("strchr_svp64 called: s: %p, c: %02x(%c)\n", s, (uint8_t)c, c);

    const char *sptr = s;
    // These cannot be the same pointer as the original function, as it is really a separate CPU/RAM
    // we have to memcpy from input to this pointer, the address was chosen arbitrarily
    uint64_t sptr_svp64  = 0x100000;

    // Create the pypowersim_state
    pypowersim_state_t *state = pypowersim_prepare();

    // Change the relevant elements, mandatory: body
    state->binary = PyBytes_FromStringAndSize(strchr_svp64_filename, strlen(strchr_svp64_filename));
    // Set GPR #REG_s to the pointer s
    PyObject *s_address = PyLong_FromUnsignedLongLong(sptr_svp64);
    PyList_SetItem(state->initial_regs, REG_s, s_address);

    // Set GPR #REG_c to the char 'c'
    PyObject *c_svp64 = PyLong_FromUnsignedLongLong(c);
    PyList_SetItem(state->initial_regs, REG_c, c_svp64);

    // Load data into buffer from real memory
    size_t bytes = strlen(s);
    size_t bytes_rem = bytes % 8;
    bytes -= bytes_rem;
    printf("bytes: %ld, bytes_rem: %ld\n", bytes, bytes_rem);
    
    uint64_t svp64_ptr = sptr_svp64;
    // Load data into buffer from real memory
    for (size_t i=0; i < bytes; i += 8) {
      PyObject *svp64_address = PyLong_FromUnsignedLongLong(svp64_ptr);
      uint64_t *sptr64 = (uint64_t *) sptr;
      /*printf("m[%ld] \t: %p -> %02x %02x %02x %02x %02x %02x %02x %02x\n", i, sptr64, sptr[0], sptr[1], sptr[2], sptr[3],
                                                                             sptr[4], sptr[5], sptr[6], sptr[7]);
      printf("val \t: %016lx -> %016lx\n", *sptr64, svp64_ptr);*/
      PyObject *word = PyLong_FromUnsignedLongLong(*sptr64);
      PyDict_SetItem(state->initial_mem, svp64_address, word);
      sptr += 8;
      svp64_ptr += 8;
    }
    // Load remaining bytes
    PyObject *svp64_address = PyLong_FromUnsignedLongLong(svp64_ptr);
    uint64_t sptr64 = 0;
    uint8_t *sptr8 = (uint8_t *) &sptr64;
    for (size_t i=0; i < bytes_rem; i++) {
        sptr8[i] = sptr[i];
        printf("%02x ", sptr8[i]);
    }
    printf("\n");
    //printf("val \t: %016lx -> %016lx\n", sptr64, svp64_ptr);
    PyObject *word = PyLong_FromUnsignedLongLong(sptr64);
    PyDict_SetItem(state->initial_mem, svp64_address, word);

    // Prepare the arguments object for the call
    pypowersim_prepareargs(state);

    // Call the function and get the resulting object
    state->result_obj = PyObject_CallObject(state->simulator, state->args);
    if (!state->result_obj) {
        PyErr_Print();
        printf("Error invoking 'run_a_simulation'\n");
        pypowersim_finalize(state);
        exit(1);
    }

    // Get the GPRs from the result_obj
    PyObject *final_regs = PyObject_GetAttrString(state->result_obj, "gpr");
    if (!final_regs) {
        PyErr_Print();
        printf("Error getting final GPRs\n");
        pypowersim_finalize(state);
        exit(1);
    }

    // GPR #REG_s holds the return value as an integer
    PyObject *key = PyLong_FromLongLong(REG_s);
    PyObject *itm = PyDict_GetItem(final_regs, key);
    if (!itm) {
        PyErr_Print();
        printf("Error getting GPR #%d\n", REG_s);
        pypowersim_finalize(state);
        exit(1);
    }
    PyObject *value = PyObject_GetAttrString(itm, "value");
    if (!value) {
        PyErr_Print();
        printf("Error getting value of GPR #%d\n", REG_s);
        pypowersim_finalize(state);
        exit(1);
    }
    uint64_t val = PyLong_AsUnsignedLongLong(value);
    printf("return val \t: %016lx\n", val);
    if (val) {
        // Return value
        char *result = (char *) s;
        printf("s         : %p\n", result);
        uint64_t offset = val - sptr_svp64;
        printf("sptr_svp64: %016lx\n", sptr_svp64);
        printf("val       : %016lx\n", val);
        printf("offset    : %016lx\n", offset);
        result += offset;
        printf("result    : %p\n", result);
        return result;
    } else {
        return NULL;
    }
    pypowersim_finalize(state);
}
#ifdef weak_alias
weak_alias (__strchr_svp64, strchr_svp64)
#endif
libc_hidden_builtin_def (strchr_svp64)
