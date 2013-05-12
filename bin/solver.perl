#!/usr/bin/perl -w
#
#  Main authors:
#     Christian Schulte
#
#  Copyright:
#     Christian Schulte, 2013
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


$dpv = "1402,490,495,487,3007,3773,653,414,1404,1901,871,2970,1177,2888,2667,2870,119,1141,700,1739,1430,1553,585,3558,763";

$downloads = 0;
foreach $d (split(',',$dpv)) {
  $downloads += $d;
}

use Time::Piece;

my $today = Time::Piece->new->strftime('%m/%d/%Y');
my $version = shift @ARGV;

my $n = 0;

$list{"regular"} = 1;

while ($l = <>) {
  while ($l =~ /(.*)\\CAT\[([^\]]*)\]{([^}]*)}{([^}]*)}{([^}]*)}(.*)/) {
    my $prefix = $1; my $suffix = $6;
    my $gcc = $3;
    my $gecode = $4;
    if ($gcc =~ /-/) {
      foreach $gcentry (split(',',$gecode)) {
        $list{$gcentry} = 1;
      }
    } else {
      foreach $gcentry (split(',',$gcc)) {
        $list{$gcentry} = 1;
      }
    }
    $l = $prefix . $suffix;
  }
}

print <<EOF
<?xml version="1.0" encoding="ISO-8859-1" ?>

<!--

   CAUTION:
     This file has been automatically generated. Do not edit!

   Main author:
      Christian Schulte <schulte\@gecode.org>

   Copyright:
      Christian Schulte, 2013

   The generated description is part of Gecode, the generic
   constraint development environment:
      http://www.gecode.org

   Permission is hereby granted, free of charge, to any person obtaining
   a copy of this software and associated documentation files (the
   "Software"), to deal in the Software without restriction, including
   without limitation the rights to use, copy, modify, merge, publish,
   distribute, sublicense, and/or sell copies of the Software, and to
   permit persons to whom the Software is furnished to do so, subject to
   the following conditions:

   The above copyright notice and this permission notice shall be
   included in all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
   LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
   OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
   WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

-->

   <questionnaire orderid="gecode" >
         <productname>Gecode</productname>
         <website>http://www.gecode.org/</website>
         <forum>http://www.gecode.org/community.html</forum>
         <implementationlanguage>C++</implementationlanguage>
         <modelinglanguage>C++, MiniZinc, AMPL</modelinglanguage>
         <supportedapis>
               <apiname>C++</apiname>
               <apiname>MiniZinc</apiname>
               <apiname>AMPL</apiname>
               <apiname>Python</apiname>
               <apiname>Prolog</apiname>
               <apiname>Haskell</apiname>
               <apiname>Ruby</apiname>
               <apiname>Common Lisp</apiname>
         </supportedapis>
         <supportedvariabletypes>
               <variabletype>integer</variabletype>
               <variabletype>Boolean</variabletype>
               <variabletype>set</variabletype>
               <variabletype>float</variabletype>
         </supportedvariabletypes>
         <supportedglobalconstraints>
               <constraint>more than 70 constraints from the Global Constraint Catalog</constraint>
               <constraint>many additional constraints not in the Global Constraint Catalog</constraint>
               <constraint>all constraints as defined by MiniZinc</constraint>
         </supportedglobalconstraints>
         <supportedsearchalgorithms>
               <algorithm>depth first (sequential and parallel)</algorithm>
               <algorithm>branch and bound (sequential and parallel)</algorithm>
               <algorithm>restart-based (sequential and parallel)</algorithm>
               <algorithm>interactive graphical</algorithm>
         </supportedsearchalgorithms>
         <supportedvariableselectors>
               <selector>static, random, by size, degree, accumulated failure count, activity, and many users</selector>
               <selector>by user-defined merit function</selector>
               <selector>tie-breaking and randomized tie-breaking</selector>
               <selector>freely programmable with documented API</selector>
         </supportedvariableselectors>
         <supportedvalueselectors>
               <selector>random, smallest, median, largest, splitting, all values</selector>
               <selector>from previous solution</selector>
               <selector>user-defined value function</selector>
               <selector>freely programmable with documented API</selector>
         </supportedvalueselectors>
         <supportedverticalproblems>
               <vertical>scheduling</vertical>
               <vertical>bin packing</vertical>
         </supportedverticalproblems>
         <licensetype>MIT license</licensetype>
         <documentation>tutorial (over 500 pages dowloadable book), reference (136 MB of html)</documentation>
         <firstreleaseyear>2005</firstreleaseyear>
         <currentrelease>$version</currentrelease>
         <downloadstotal>$downloads, also included in Linux distributions (Debian, Ubuntu, Gentoo, OpenSUSE, ...) and FreeBSD</downloadstotal>
	 <awards>all gold medals in all categories at MiniZinc challenges 2008-2012</awards>
         <additionalcomments>
               <comment>support for automatic symmetry breaking during search (LDSB)</comment>
               <comment>documented C++ APIs for: modeling, implementing constraints, implementing branchers, implementing search engines, implementing new variable types</comment>
         </additionalcomments>
         <submittedby>Christian Schulte</submittedby>
         <submittedwhen>$today</submittedwhen>
         <email>schulte\@gecode.org</email>
         <organization>Gecode Team</organization>
         <position>development lead</position>
   </questionnaire>
EOF
;
