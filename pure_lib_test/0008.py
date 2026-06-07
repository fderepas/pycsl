#!/usr/bin/env python3
"""Concrete test 0008 — tests for new stdlib modules (Phases 1-3).

Based on library_reference/ descriptions:
- colorsys: RGB/HSV/HLS conversions are pure arithmetic in [0,1]
- html: escape() grows strings, unescape() shrinks/preserves
- textwrap: wrap yields lines, dedent/indent are inverse-ish
- string: capwords capitalizes words, Template substitutes
- signal: constants are positive integers
- struct: calcsize returns non-negative sizes
- linecache: getline returns line content or empty
- abc: abstractmethod is identity decorator
- heapq: push grows, pop shrinks, nlargest/nsmallest bounded
- pprint: pformat returns string repr
- csv: field counting and row writing
- getopt: parse count bounded by argc
- numbers: gcd, mod, floordiv basic properties
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

passed = 0
failed = 0

def check(name, cond):
    global passed, failed
    if cond:
        print(f"PASS: {name}")
        passed += 1
    else:
        print(f"FAIL: {name}")
        failed += 1

# --- colorsys (csys) ---
from pure_lib.csys import rgb_to_yiq_y, rgb_max, rgb_min, saturation, hsv_p, hls_to_rgb_helper, hls_m2

check("yiq_y pure black", rgb_to_yiq_y(0, 0, 0) == 0)
check("yiq_y pure white", rgb_to_yiq_y(1000, 1000, 1000) == 1000)
check("yiq_y red component", rgb_to_yiq_y(1000, 0, 0) == 300)
check("rgb_max basic", rgb_max(100, 500, 300) == 500)
check("rgb_min basic", rgb_min(100, 500, 300) == 100)
check("saturation zero max", saturation(0, 0) == 0)
check("saturation full", saturation(1000, 0) == 1000)
check("saturation half", saturation(1000, 500) == 500)
check("hsv_p basic", hsv_p(1000, 0) == 1000)
check("hsv_p full sat", hsv_p(1000, 1000) == 0)
check("hls_m2 low l", hls_m2(200, 500) == 300)
check("hls_to_rgb_helper no sat", hls_to_rgb_helper(500, 500, 0) == 500)

# --- html (htmlm) ---
from pure_lib.htmlm import escape, unescape, escape_quote

check("escape non-negative", escape(10) >= 0)
check("escape preserves", escape(5) == 5)
check("unescape non-negative", unescape(10) >= 0)
check("escape_quote monotone", escape_quote(7) >= 7)

# --- textwrap (txtwrp) ---
from pure_lib.txtwrp import wrap, fill, shorten, dedent, indent

check("wrap empty", wrap(0, 80) == 0)
check("wrap one line", wrap(40, 80) == 1)
check("wrap two lines", wrap(160, 80) == 2)
check("fill preserves", fill(100, 80) == 100)
check("shorten within width", shorten(50, 80) == 50)
check("shorten truncates", shorten(100, 80) == 80)
check("dedent preserves/shrinks", dedent(50) <= 50)
check("indent grows", indent(50, 4) >= 50)

# --- string (strmod) ---
from pure_lib.strmod import capwords, template_substitute, template_safe_substitute, format_field

check("capwords preserves/shrinks", capwords(20) <= 20)
check("template_substitute", template_substitute(10, 5) == 15)
check("template_safe_substitute", template_safe_substitute(10, 5) == 15)
check("format_field zero fmt", format_field(0, 5) == 5)
check("format_field nonzero", format_field(3, 5) == 8)

# --- signal (sig) ---
from pure_lib.sig import SIGINT, SIGTERM, SIGKILL, signal_handler, getsignal, valid_signals_count

check("SIGINT is 2", SIGINT == 2)
check("SIGTERM is 15", SIGTERM == 15)
check("SIGKILL is 9", SIGKILL == 9)
check("signal_handler returns default", signal_handler(2, 1) == 0)
check("getsignal returns default", getsignal(15) == 0)
check("valid_signals_count", valid_signals_count() == 64)

# --- struct (strct) ---
from pure_lib.strct import calcsize, pack, unpack, unpack_from

check("calcsize non-negative", calcsize(8) >= 0)
check("pack result", pack(4, 42) == 4)
check("unpack result", unpack(2, 8) == 2)
check("unpack_from result", unpack_from(3, 16, 0) == 3)

# --- linecache (lcache) ---
from pure_lib.lcache import getline, getlines, clearcache, checkcache

check("getline result", getline(1, 1) >= 0)
check("getlines result", getlines(10) >= 0)
clearcache()
check("clearcache runs", True)
check("checkcache result", checkcache(5) >= 0)

# --- abc (abcmod) ---
from pure_lib.abcmod import abstractmethod, update_abstractmethods

check("abstractmethod identity", abstractmethod(42) == 42)
check("update_abstractmethods identity", update_abstractmethods(7) == 7)

# --- heapq (hq) ---
from pure_lib.hq import heappush, heappop, heapreplace, heapify, nlargest, nsmallest, heappushpop

check("heappush grows", heappush(5, 3) == 6)
check("heappop shrinks", heappop(5) == 4)
check("heapreplace same size", heapreplace(5, 3) == 5)
check("heapify same size", heapify(10) == 10)
check("nlargest bounded by k", nlargest(3, 10) == 3)
check("nlargest bounded by n", nlargest(20, 5) == 5)
check("nsmallest bounded", nsmallest(3, 10) == 3)
check("heappushpop same size", heappushpop(5, 3) == 5)

# --- pprint (pp) ---
from pure_lib.pp import pformat, saferepr, isreadable, isrecursive

check("pformat non-negative", pformat(10) >= 0)
check("saferepr non-negative", saferepr(5) >= 0)
check("isreadable returns 0/1", isreadable(3) in (0, 1))
check("isrecursive returns 0/1", isrecursive(3) in (0, 1))

# --- csv (csvmod) ---
from pure_lib.csvmod import count_fields, write_row, reader_count, writerows

check("count_fields empty", count_fields(0) == 0)
check("count_fields non-empty", count_fields(10) >= 1)
check("write_row", write_row(5) >= 5)
check("reader_count", reader_count(100) >= 0)
check("writerows", writerows(10, 3) == 30)

# --- getopt (gopt) ---
from pure_lib.gopt import getopt_count, gnu_getopt_count, remaining_args

check("getopt_count bounded", getopt_count(5, 3) <= 5)
check("gnu_getopt_count bounded", gnu_getopt_count(5, 3) <= 5)
check("remaining_args", remaining_args(5, 3) == 2)
check("remaining_args excess", remaining_args(3, 5) == 0)

# --- numbers (nums) ---
from pure_lib.nums import to_int, mod, floordiv, rational_num, rational_den, gcd

check("to_int identity", to_int(42) == 42)
check("mod basic", mod(7, 3) == 1)
check("mod zero", mod(6, 3) == 0)
check("floordiv basic", floordiv(7, 3) == 2)
check("rational_num", rational_num(3, 4) == 3)
check("rational_den", rational_den(3, 4) == 4)
check("gcd both zero", gcd(0, 0) == 0)
check("gcd one zero", gcd(0, 5) == 5)
check("gcd commutative bound", gcd(6, 4) <= 6)

# --- Summary ---
print(f"\n{passed} passed, {failed} failed out of {passed + failed}")
if failed:
    sys.exit(1)
