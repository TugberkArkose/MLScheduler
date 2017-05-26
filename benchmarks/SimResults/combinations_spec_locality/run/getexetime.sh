#!/bin/bash
for p in pinned fair tlss hrrs;
do
  echo $p;
  for i in bwavesgcccactusADMsoplex bwavesgcccactusADMastar bwavesgcccactusADMmilc bwavesgcccactusADMgromacs bwavesgccmcfhmmer bwavesgccmcfleslie3d bwavesGemsFDTDastaromnetpp soplexmcfcalculixgcc perlbenchgamessbzip2calculix astarlbmtontoh264ref namdgromacscalculixcactusADM zeusmpxalancbmknamdgobmk sjengpovrayomnetppmilc calculixlibquantumzeusmpsjeng sjengleslie3dgobmkmilc astarzeusmpcactusADMGemsFDTD povraygromacslibquantumbzip2 ;
  do
    var=$(cat $p$i/sim.out | grep Time | tr '|' '\n' | tail -4 | sort -n | tail -1) ;
    echo $i $var;
  done
done