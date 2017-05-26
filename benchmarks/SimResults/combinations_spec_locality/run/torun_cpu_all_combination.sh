#!/bin/sh
qsub -l big cmp_bwavesgcccactusADMsoplex.sh
qsub -l big cmp_bwavesgcccactusADMastar.sh
qsub -l big cmp_bwavesgcccactusADMmilc.sh
qsub -l big cmp_bwavesgcccactusADMgromacs.sh
qsub -l big cmp_bwavesgccmcfhmmer.sh
qsub -l big cmp_bwavesgccmcfleslie3d.sh
qsub -l big cmp_bwavesGemsFDTDastaromnetpp.sh
qsub -l big cmp_soplexmcfcalculixgcc.sh
qsub -l big cmp_perlbenchgamessbzip2calculix.sh
qsub -l big cmp_astarlbmtontoh264ref.sh
qsub -l big cmp_namdgromacscalculixcactusADM.sh
qsub -l big cmp_zeusmpxalancbmknamdgobmk.sh
qsub -l big cmp_sjengpovrayomnetppmilc.sh
qsub -l big cmp_calculixlibquantumzeusmpsjeng.sh
qsub -l big cmp_sjengleslie3dgobmkmilc.sh
qsub -l big cmp_astarzeusmpcactusADMGemsFDTD.sh
qsub -l big cmp_povraygromacslibquantumbzip2.sh
