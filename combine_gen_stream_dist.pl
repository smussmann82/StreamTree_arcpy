#!/usr/bin/perl

use warnings;
use strict;
use Data::Dumper;

my $file = "gendist_pairs.txt";
my $paths = "allpaths.txt";

my @pairs;
my @paths;
my @outlines;
my %hash;

my %pophash;
my %seghash;
my %pathhash;

open(FILE, $file) or die "Can't open $file: $!\n\n";
	while(my $line = <FILE>){
		chomp $line;
		push @pairs, $line;
	}
close FILE;

open( FILE, $paths ) or die "Can't open $paths: $!\n\n";
	while(my $line = <FILE>){
		chomp $line;
		push @paths, $line;
	}
close FILE;

foreach my $path( @paths ){
	my @temp = split(/,/, $path);
	my $pop1 = shift( @temp );
	my $pop2 = shift( @temp );
	
	$pathhash{$pop1}{$pop2} = join( ",", @temp );
	$pathhash{$pop2}{$pop1} = join( ",", reverse( @temp ) );
}

#put genetic distances into hash
foreach my $pair( @pairs ){
	my @temp = split( /\s+/, $pair);
	if($temp[2] < 0){
		$temp[2] = 0.0;
	}
	$pophash{$temp[0]}++;
	$pophash{$temp[1]}++;
	$hash{$temp[0]}{$temp[1]} = $temp[2];
	$hash{$temp[1]}{$temp[0]} = $temp[2];
}

my @pops;
foreach my $key( sort {lc($a) cmp lc($b)} keys %pophash ){
	push @pops, $key;
}

for( my $i=0; $i<@pops; $i++ ){
	for( my $j=$i+1; $j<@pops; $j++ ){
		my $curline = $pops[$i] . " " . $pops[$j] . "\t" . $hash{$pops[$i]}{$pops[$j]};
		my @temp = split( /,/, $pathhash{$pops[$i]}{$pops[$j]} );
		foreach my $segment( @temp ){
			$seghash{$segment}++;
			$curline .= "\t";
			$curline .= $segment;
		}
		$curline .= "\n";
		push @outlines, $curline;
	}
	
}

my %segmap;
my $counter = 0;
foreach my $key( sort {$a <=> $b} keys %seghash ){
	$counter++;
	$segmap{$key} = $counter;
}

for(my $i=0; $i<@outlines; $i++){
	chomp($outlines[$i]);
	my @temp = split( /\s+/, $outlines[$i] );
	for(my $j=3; $j<@temp; $j++){
		$temp[$j] = $segmap{$temp[$j]};
	}
	push @temp, "\n";
	my $string = join("\t", @temp);
	$outlines[$i] = $string;
}

open( OUT, '>', "streamtree_input.txt" ) or die "Can't open streamtree_input.txt: $!\n\n";

print OUT "TITLE = SPD StreamTree Data\n";
print OUT "SAMPLES = ";

my $string = join( ", ", @pops );

print OUT $string, "\n";
print OUT "NSECTIONS = ";
print OUT scalar(keys %seghash), "\n";

foreach my $line( @outlines ){
	print OUT $line;
}

close OUT;

print Dumper(\%hash);

print scalar( keys %pophash), "\n";
print scalar( keys %seghash), "\n";

exit;
