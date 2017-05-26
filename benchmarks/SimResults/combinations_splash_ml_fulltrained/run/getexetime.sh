#!/bin/bash
for p in pinned fair hrrs tlss;
do
  echo $p;
  for i in choleskybarnesfftfmm choleskybarnesfftocean.cont choleskybarnesfftraytrace choleskybarnesfftwater.sp choleskybarnesradiositylu.cont choleskybarnesradiosityocean.ncont ;
  do
    var=$(cat $p$i/sim.out | grep Time | tr '|' '\n' | tail -4 | sort -n | tail -1) ;
    echo $i $var;
  done
done