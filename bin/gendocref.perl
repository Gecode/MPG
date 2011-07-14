#!/usr/bin/perl
#
#  Main authors:
#     Christian Schulte <schulte@gecode.org>
#
#  Copyright:
#     Christian Schulte, 2009
#
#  Last modified:
#     $Date: 2008-09-03 14:14:11 +0200 (Wed, 03 Sep 2008) $ by $Author: tack $
#     $Revision: 7787 $
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

$gecode = $ARGV[0];

open TAGFILE, "$gecode/doc/gecode-doc.tag";

while ($l = <TAGFILE>) {
  if ($l =~ /<compound kind="file">/) {
    my $name;
    my $path;
    my $url;
    while (($l = <TAGFILE>) && !($l =~ /<\/compound>/)) {
      if (($l =~ /<name>(.*)<\/name>/) && !$name) {
	$name = &ceify($1);
      } elsif (($l =~ /<filename>(.*)<\/filename>/) && !$url) {
	$url = $1;
      } elsif (($l =~ /<path>(.*)<\/path>/) && !$url) {
	$fullpath = $1;
	$path = $fullpath;
	if ($path =~ /.*\/(test\/.*)/) {
	  $path = $1;
	} elsif ($path =~ /.*\/(examples\/.*)/) {
	  $path = $1;
	} elsif ($path =~ /.*gecode.*\/(gecode\/.*)/) {
	  $path = $1;
	} elsif ($path =~ /.*\/(.*)/) {
	  $path = $1;
	}
      }
    }
    if (($path =~ /^examples\//) && ($name =~ /\.cpp$/)) {
      my $t; my $c;
      $basename = $name;
      $basename =~ s|\..*||g;
      open(EXAMPLE, "$gecode/$path$name");
      while ($e = <EXAMPLE>) {
	if ($e =~ /\%Example: (.*)/) {
	  $t = $1;
	  $t =~ s|\%||g;
	} elsif ($e =~ /class ([a-zA-Z_]+) :/) {
	  $c = $1;
	  $url{"example $basename:$c"} = "$url.html";
	  $title{"example $basename:$c"} = "$t";
	}
      }
      close EXAMPLE;
      $url{"example $basename"} = "$url.html";
      $title{"example $basename"} = "$t";
    }
    $url{"file $path$name"} = "$url.html";
  } elsif ($l =~ /<compound kind="group">/) {
    my $name;
    my $url;
    my $title;
    while (($l = <TAGFILE>) && !($l =~ /<\/compound>/)) {
      if (($l =~ /<name>(.*)<\/name>/) && !$name) {
	$name = &ceify($1);
      } elsif (($l =~ /<filename>(.*)<\/filename>/) && !$url) {
	$url = $1;
      } elsif (($l =~ /<title>(.*)<\/title>/) && !$url) {
	$title = $1;
	$title =~ s|\%||g;
      }
    }
    $url{"group $name"} = "$url";
    $title{"group $name"} = "$title";
  } elsif ($l =~ /<compound kind="page">/) {
    my $name;
    my $url;
    my $title;
    while (($l = <TAGFILE>) && !($l =~ /<\/compound>/)) {
      if (($l =~ /<name>(.*)<\/name>/) && !$name) {
	$name = &ceify($1);
      } elsif (($l =~ /<filename>(.*)<\/filename>/) && !$url) {
	$url = $1;
      } elsif (($l =~ /<title>(.*)<\/title>/) && !$url) {
	$title = $1;
	$title =~ s|\%||g;
      }
    }
    $url{"page $name"} = "${url}.html";
    $title{"page $name"} = "$title";
  } elsif ($l =~ /<compound kind="class">/) {
    my $name;
    my $url;
    while (($l = <TAGFILE>) && !($l =~ /<\/compound>/)) {
      if (($l =~ /<name>(.*)<\/name>/) && !$name) {
	$name = &ceify($1);
      } elsif (($l =~ /<filename>(.*)<\/filename>/) && !$url) {
	$url = $1;
      }
    }
    $url{"class $name"} = "$url";
  } elsif ($l =~ /<compound kind="namespace">/) {
    my $name;
    my $url;
    while (($l = <TAGFILE>) && !($l =~ /<\/compound>/)) {
      if (($l =~ /<name>(.*)<\/name>/) && !$name) {
	$name = &ceify($1);
      } elsif (($l =~ /<filename>(.*)<\/filename>/) && !$url) {
	$url = $1;
      }
    }
    $url{"namespace $name"} = "$url";
  }
}


close TAGFILE;

for $u (sort(keys(%url))) {
  print "URL $u $url{$u}\n";
  if ($title{$u}) {
    print "TITLE $u \"$title{$u}\"\n";
  }
}

sub ceify {
  my $n = $_[0];
  $n =~ s|\&lt;|<|g;
  $n =~ s|\&gt;|>|g;
  $n =~ s| ||g;
  $n =~ s|\%||g;
  return $n;
}
