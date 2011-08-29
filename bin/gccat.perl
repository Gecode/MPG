#!/usr/bin/perl -w
#
#  Main authors:
#     Christian Schulte <schulte@gecode.org>
#
#  Copyright:
#     Christian Schulte, 2011
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

$version = shift @ARGV;
$year    = shift @ARGV;
$type    = shift @ARGV;

open(DBFILE, "<", "bin/gl.db");
while ($e = <DBFILE>) {
  if ($e =~ /URL (.*) (.*) (.*)/) {
    $url{$1}{$2} = $3;
  } elsif ($e =~ /TITLE (.*) (.*) \"(.*)\"/) {
    $title{$1}{$2} = $3;
  }
}
close(DBFILE);

$gccaturl  = "http://www.emn.fr/z-info/sdemasse/gccat/C";
$gecodeurl = "http://www.gecode.org/doc-$version/reference/";

# Extract Global Constraint Catalog information
while ($l = <>) {
  chop($l);
  if ($l =~ /\\label\{(sec:m:.*)\}/) {
    $label = $1;
  }
  if ($l =~ /\\CAT\[([^\]]*)\]{([^}]*)}{([^}]*)}{([^}]*)}/) {
    my $section = $1; my $gccnames = $2; my $gecodename = $3; my $ref = $4;
    foreach $gce (split(',',$gccnames)) {
      my $key = "$gce-$section";
      $gces{$gce} = 1;
      $gcentry{$key}  = $gce;
      $section{$key}  = $section;
      $caturl{$key}   = $gccaturl . $gce . ".html";
      $mpg{$key}      = $label;
      $gecode{$key}   = $gecodename;
      $docurl{$key}   = $gecodeurl . $url{"group"}{$ref};
      $doctitle{$key} = $title{"group"}{$ref};
    }
  }
}

if ($type =~ /prolog/) {
  print <<EOF
%%
%% Mapping of GCCAT names to Gecode names
%%
%% Corresponding to Gecode version: $version
%%
%% Copyright: Christian Schulte <schulte\@gecode.org>, $year
%%
%%  Permission is hereby granted, free of charge, to any person obtaining
%%  a copy of this software and associated documentation files (the
%%  "Software"), to deal in the Software without restriction, including
%%  without limitation the rights to use, copy, modify, merge, publish,
%%  distribute, sublicense, and/or sell copies of the Software, and to
%%  permit persons to whom the Software is furnished to do so, subject to
%%  the following conditions:
%%
%%  The above copyright notice and this permission notice shall be
%%  included in all copies or substantial portions of the Software.
%%
%%  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
%%  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
%%  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
%%  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
%%  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
%%  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
%%  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
%%

EOF
  ;

  foreach $e (sort(keys(%gces))) {
    if (!($e =~ /^-/)) {
      print "ctr_systems('$e',[";
      my $fst = 1;
      foreach $k (keys(%gcentry)) {
	if ($gcentry{$k} eq $e) {
          if ($fst) {
	    $fst = 0;
	  } else {
	    print ",";
	  }
	  print "\n  gecode('" . $gecode{$k} . "','";
	  print $docurl{$k} . "')";
	}
      }
      print "\n]).\n\n";
    }
  }
}
