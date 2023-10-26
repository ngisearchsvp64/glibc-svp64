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

#ifndef _LIBC
# include <config.h>
#endif

#include <string.h>

#include <stddef.h>

#include <limits.h>

#undef __memchr_svp64_real
#ifdef _LIBC
# undef memchr_svp64_real
#endif

#ifndef weak_alias
# define __memchr_svp64_real memchr_svp64_real
#endif

#ifndef MEMCHR_SVP64
# define MEMCHR_SVP64_REAL __memchr_svp64_real
#endif

/* Search no more than N bytes of S for C.  */
char*
MEMCHR_SVP64_REAL (const char *s, int c, size_t n)
{
  while (n--)
    if (*s++ == (char) c)
      return (char *) s - 1;
  return NULL;
}
#ifdef weak_alias
weak_alias (__memchr_svp64_real, memchr_svp64_real)
#endif
libc_hidden_builtin_def (memchr_svp64_real)
