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

$c_title = "";

while ($l = <>) {
  if ($l =~ /\\chapter\{(.*)\}/) {
    $c_title = $1;
  } elsif ($l =~ /\\chapter\[(.*)\]\{(.*)\}/) {
    $c_title = $1;
  } elsif ($l =~ /\\section\{(.*)\}/) {
    $s_title = $1;
  } elsif ($l =~ /\\label\{chap:(.:.*)\}/) {
    $label = $1;
    $c{$label} = $c_title;
  } elsif ($l =~ /\\label\{sec:(m:.*)\}/) {
    $label = $1;
    $s{$label} = $s_title;
  }
}

foreach $l (sort(keys(%c))) {
  $cmd = $l;
  $cmd =~ s|:||og;
  $cmd =~ s|_||og;
  $cmd =~ s|-||og;
#  print "\\newcommand\{\\tc$cmd\}\{\\autoref\{chap:$l\} (" . $c{$l} . ")\}\n";
  print "\\newcommand\{\\tc$cmd\}\{\\hyperref[chap:$l]\{\\autoref*\{chap:$l\} (" . $c{$l} . ")\}\}\n\n";
}
foreach $l (sort(keys(%s))) {
  $cmd = $l;
  $cmd =~ s|:||og;
  $cmd =~ s|_||og;
  $cmd =~ s|-||og;
#  print "\\newcommand\{\\ts$cmd\}\{\\autoref\{sec:$l\} (" . $s{$l} . ")\}\n";
#  print "\\newcommand\{\\pts$cmd\}\{(\\autoref\{sec:$l\} " . $s{$l} . ")\}\n";
  print "\\newcommand\{\\ts$cmd\}\{\\autoref\{sec:$l\}\}\n";
  print "\\newcommand\{\\pts$cmd\}\{(\\autoref\{sec:$l\})\}\n";
}
