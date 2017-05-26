#!/bin/bash
for p in pinned fair hrrs tlss;
do
  echo $p;
  for i in barnes barnes barnes barnes barnes barnes barnes barnes barnes barnes barnes barnes cholesky cholesky cholesky cholesky cholesky cholesky cholesky cholesky cholesky cholesky cholesky fft fft fft fft fft fft fft fft fft fft fmm fmm fmm fmm fmm fmm fmm fmm fmm lu.cont lu.cont lu.cont lu.cont lu.cont lu.cont lu.cont lu.cont lu.ncont lu.ncont lu.ncont lu.ncont lu.ncont lu.ncont lu.ncont ocean.cont ocean.cont ocean.cont ocean.cont ocean.cont ocean.cont ocean.ncont ocean.ncont ocean.ncont ocean.ncont ocean.ncont radiosity radiosity radiosity radiosity radix radix radix raytrace raytrace water.nsq ;
  do
    var=$(cat $p$i/sim.out | grep Time | tr '|' '\n' | tail -4 | sort -n | tail -1) ;
    echo $i $var;
  done
done