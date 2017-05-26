#!/bin/bash
echo $p;
for i in */ ;
do
  var=$(cat $i/sim.out | grep Time | tr '|' '\n' | tail -4 | sort -n | tail -1) ;
  echo $i $var;
done
