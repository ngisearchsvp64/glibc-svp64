/* Copyright 2023 VectorCamp
   Copyright 2023 Red Semiconductor Ltd.
   Funded by NGI Search Programme HORIZON-CL4-2021-HUMAN-01 2022,
   https://www.ngisearch.eu/, EU Programme 101069364.

   Copyright (C) 1991-2018 Free Software Foundation, Inc.
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

#ifndef _LIBC
# include <config.h>
#endif

#include <string.h>

#include <stddef.h>

#include <limits.h>

#undef __memrchr_svp64
#ifdef _LIBC
# undef memrchr_svp64
#endif

#ifndef weak_alias
# define __memrchr_svp64 memrchr_svp64
#endif

#ifndef memrchr_SVP64
# define MEMRCHR_SVP64 __memrchr_svp64
#endif

#include <Python.h>
#include <stdint.h>
#include <stdio.h>

#include "pypowersim_wrapper_common.h"

const char *memrchr_svp64_filename = "./bin/memrchr_svp64.bin";

/* Starting from the end, search no more than N bytes of S for C.  */
char*
MEMRCHR_SVP64 (const char *s, int c, size_t n)
{
    printf("memrchr_svp64 called: s: %p, c: %02x(%c), n: %ld\n", s, (uint8_t)c, c, n);

    const char *sptr = s;
    // These cannot be the same pointer as the original function, as it is really a separate CPU/RAM
    // we have to memcpy from input to this pointer, the address was chosen arbitrarily
    uint64_t sptr_svp64  = 0x100000;

    // Create the pypowersim_state
    pypowersim_state_t *state = pypowersim_prepare();

    // Change the relevant elements, mandatory: body
    state->binary = PyBytes_FromStringAndSize(memrchr_svp64_filename, strlen(memrchr_svp64_filename));
    // Set GPR #3 to the pointer s
    PyObject *s_address = PyLong_FromUnsignedLongLong(sptr_svp64);
    PyList_SetItem(state->initial_regs, 3, s_address);

    // Set GPR #4 to the char 'c'
    PyObject *c_svp64 = PyLong_FromUnsignedLongLong(c);
    PyList_SetItem(state->initial_regs, 4, c_svp64);

    // Set GPR #5 length of string in bytes 'n'
    PyObject *n_svp64 = PyLong_FromUnsignedLongLong(n);
    PyList_SetItem(state->initial_regs, 5, n_svp64);

    // Load data into buffer from real memory
    size_t bytes = n;
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
        printf("%02x ", sptr[i]);
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

    // GPR #3 holds the return value as an integer
    PyObject *key = PyLong_FromLongLong(3);
    PyObject *itm = PyDict_GetItem(final_regs, key);
    if (!itm) {
        PyErr_Print();
        printf("Error getting GPR #3\n");
        pypowersim_finalize(state);
        exit(1);
    }
    PyObject *value = PyObject_GetAttrString(itm, "value");
    if (!value) {
        PyErr_Print();
        printf("Error getting value of GPR #3\n");
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
weak_alias (__memrchr_svp64, memrchr_svp64)
#endif
libc_hidden_builtin_def (memrchr_svp64)
