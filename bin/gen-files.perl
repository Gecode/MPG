#!/usr/bin/perl -w
#
#  Main authors:
#     Christian Schulte <schulte@gecode.org>
#
#  Copyright:
#     Christian Schulte, 2009
#
#  Last modified:
#     $Date: 2008-04-28 17:47:23 +0200 (Mo, 28 Apr 2008) $ by $Author: raphael $
#     $Revision: 6797 $
#
#  This file is part of Gecode, the generic constraint
#  development environment:
#     http://www.gecode.org
#
#  Permission is hereby granted, free of charge, to any person obtaining
#  a copy of this software and associated documentation files (the
#  "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so, subject to
#  the following conditions:
#
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
#  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
#  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#

$pre = pop @ARGV;

$part{"12"} = "M";
$part{"2"}  = "C";
$part{"15"} = "P";
$part{"1"}  = "B";
$part{"21"} = "V";
$part{"18"} = "S";

$p_t = "";
$c_n = 0; $c_t = "";
$s_n = 0; $s_t = "";

while ($l = <>) {
  if ($l =~ /\\mypart\{(.*)\}\{(.*)\}/) {
    $p_t = $part{$1} . " " . $2;
    $p_only = 0;
  } elsif ($l =~ /\\chapter\{(.*)\}/) {
    $c_n++; $c_t = $1; $s_n = 0;
    $c_only = 0;
  } elsif ($l =~ /\\chapter\[(.*)\]\{(.*)\}/) {
    $c_n++; $c_t = $1; $s_n = 0;
    $c_only = 0;
  } elsif ($l =~ /\\section\{(.*)\}/) {
    $t = $1;
    $t =~ s|\\CppInline\{(.*)\}|$1|g;
    $s_n++; $s_t = $t;
  } elsif ($l =~ /\%\% FILES: PARTONLY/) {
    $p_only = 1;
  } elsif ($l =~ /\%\% FILES: CHAPTERONLY/) {
    $c_only = 1;
  } elsif ($l =~ /\\litfile\{.*\}\{.*\}\{([a-z -]+)\.(cpp|hh|vis)\}\\\\/) {
    if ($p_only) {
      $d = $p_t;
    } elsif ($c_only) {
      $d = "$p_t/$c_n $c_t";
    } else {
      $d = "$p_t/$c_n $c_t/$c_n.$s_n $s_t";
    }
    system("mkdir -p \"$d\"");
    system("cp \"$pre/$1.$2\" \"$d\"");
  }
}

