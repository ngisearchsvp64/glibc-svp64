/* Test memchr functions.
   Copyright (C) 1999-2018 Free Software Foundation, Inc.
   This file is part of the GNU C Library.
   Written by Jakub Jelinek <jakub@redhat.com>, 1999.

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

#define TEST_MAIN
#ifndef WIDE
# define TEST_NAME "memchr"
#else
# define TEST_NAME "wmemchr"
#endif /* WIDE */

#include "test-string.h"
#include <stdint.h>

#ifndef WIDE
# define MEMCHR memchr
# define CHAR char
# define UCHAR unsigned char
# define SIMPLE_MEMCHR simple_memchr
# define BIG_CHAR CHAR_MAX
# define SMALL_CHAR 127
#else
# include <wchar.h>
# define MEMCHR wmemchr
# define CHAR wchar_t
# define UCHAR wchar_t
# define SIMPLE_MEMCHR simple_wmemchr
# define BIG_CHAR WCHAR_MAX
# define SMALL_CHAR 1273
#endif /* WIDE */

# define MEMCHR_SVP64 memchr_svp64

#define MAX_SIZE    256

typedef CHAR *(*proto_t) (const CHAR *, int, size_t);
CHAR *SIMPLE_MEMCHR (const CHAR *, int, size_t);
CHAR *MEMCHR_SVP64 (const CHAR *, int, size_t);

//IMPL (MEMCHR, 0)
IMPL (MEMCHR_SVP64, 1)
IMPL (SIMPLE_MEMCHR, 2)

CHAR *
SIMPLE_MEMCHR (const CHAR *s, int c, size_t n)
{
  printf("memchr called: s: %p, c: %02x(%c), n: %lu\n", s, (uint8_t)c, c, n);
  while (n--) {
    if (*s++ == (CHAR) c)
      return (CHAR *) s - 1;
  }
  return NULL;
}

static void
do_one_test (impl_t *impl, const CHAR *s, int c, size_t n, CHAR *exp_res)
{
  CHAR *res = CALL (impl, s, c, n);
  if (res != exp_res)
    {
      error (0, 0, "Wrong result in function %s %p %p", impl->name,
	     res, exp_res);
      ret = 1;
      return;
    }
}

static void
do_test (size_t align, size_t pos, size_t len, size_t n, int seek_char)
{
  size_t i;
  CHAR *result;

  if ((align + len) * sizeof (CHAR) >= page_size)
    return;

  CHAR *buf = (CHAR *) (buf1);

  for (i = 0; i < len; ++i)
    {
      buf[align + i] = 1 + 23 * i % SMALL_CHAR;
      if (buf[align + i] == seek_char)
	buf[align + i] = seek_char + 1;
    }
  buf[align + len] = 0;

  if (pos < len)
    {
      buf[align + pos] = seek_char;
      buf[align + len] = -seek_char;
      result = (CHAR *) (buf + align + pos);
    }
  else
    {
      result = NULL;
      buf[align + len] = seek_char;
    }

  FOR_EACH_IMPL (impl, 0)
    do_one_test (impl, (CHAR *) (buf + align), seek_char, n, result);
}

static void
do_random_tests (void)
{
  size_t i, j, n, align, pos, len;
  int seek_char;
  CHAR *result;
  UCHAR *p = (UCHAR *) (buf1 + page_size) - 512;

  for (n = 0; n < ITERATIONS; n++)
    {
      align = random () & 15;
      pos = random () & 511;
      if (pos + align >= 512)
	pos = 511 - align - (random () & 7);
      len = random () & 511;
      if (pos >= len)
	len = pos + (random () & 7);
      if (len + align >= 512)
	len = 512 - align - (random () & 7);
      seek_char = random () & BIG_CHAR;
      j = len + align + 64;
      if (j > 512)
	j = 512;

      for (i = 0; i < j; i++)
	{
	  if (i == pos + align)
	    p[i] = seek_char;
	  else
	    {
	      p[i] = random () & BIG_CHAR;
	      if (i < pos + align && p[i] == seek_char)
		p[i] = seek_char + 13;
	    }
	}

      if (pos < len)
	{
	  size_t r = random ();
	  if ((r & 31) == 0)
	    len = ~(uintptr_t) (p + align) - ((r >> 5) & 31);
	  result = (CHAR *) (p + pos + align);
	}
      else
	result = NULL;

      FOR_EACH_IMPL (impl, 1)
	if (CALL (impl, (CHAR *) (p + align), seek_char, len) != result)
	  {
	    error (0, 0, "Iteration %zd - wrong result in function %s (%zd, %d, %zd, %zd) %p != %p, p %p",
		   n, impl->name, align, seek_char, len, pos,
		   CALL (impl, (CHAR *) (p + align), seek_char, len),
		   result, p);
	    ret = 1;
	  }
    }
}

int
test_main (void)
{
  size_t i, j;

  test_init ();

  printf ("%20s", "");
  FOR_EACH_IMPL (impl, 0)
    printf ("\t%s", impl->name);
  putchar ('\n');

  for (i = 1; i < 2; ++i)
    {
      /* Test n == 0.  */
      do_test (i, i, 0, 0, 23);
      do_test (i, i, 0, 0, 0);

      do_test (0, 16 << i, 1024, 1024, 23);
      do_test (i, 64, 256, 256, 23);
      do_test (0, 16 << i, 1024, 1024, 0);
      do_test (i, 64, 256, 256, 0);

      /* Check for large input sizes and for these cases we need to
	 make sure the byte is within the size range (that's why
	 7 << i must be smaller than 1024).  */
      do_test (0, 7 << i, 1024, MAX_SIZE, 23);
      do_test (0, 1024 - i, 1024, MAX_SIZE, 23);
      do_test (i, 64, 256, MAX_SIZE, 23);
      do_test (0, 7 << i, 1024, MAX_SIZE, 0);
      do_test (0, 1024 - i, 1024, MAX_SIZE, 0);
      do_test (i, 64, 256, MAX_SIZE, 0);
    }

  for (i = 1; i < 64; ++i)
    {
      for (j = 1; j < 64; j++)
        {
	  do_test (0, 64 - j, 64, MAX_SIZE, 23);
	  do_test (i, 64 - j, 64, MAX_SIZE, 23);
        }
    }

  for (i = 1; i < 8; ++i)
    {
      do_test (0, i, i + 1, i + 1, 23);
      do_test (0, i, i + 1, i + 1, 0);
    }

  /* BZ#21182 - wrong overflow calculation for i686 implementation
     with address near end of the page.  */
  for (i = 2; i < 16; ++i)
    /* page_size is in fact getpagesize() * 2.  */
    do_test (page_size / 2 - i, i, i, 1, 0x9B);

  do_random_tests ();
  return ret;
}

#include <support/test-driver.c>
