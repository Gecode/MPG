#!/usr/bin/perl -w

$i=22;
while ($l = <>) {
  chomp($l);
  $l =~ s|[\t ]*||g;
  print "% $l\n";
  @cs = split(//,$l);
  $j=0;
  foreach $c (@cs) {
    if ($c eq "*") {
      print "\\bfield{$j}{$i}";
    } else {
      print "\\sol{$j}{$i}{$c}";
    }
    $j++;
  }
  print "\n";
  $i--;
}
