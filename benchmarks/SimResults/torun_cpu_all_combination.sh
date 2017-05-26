#!/bin/sh
qsub -l big cmp_bwavesgcccactusADMsoplex.sh
qsub -l big cmp_bwavesgcccactusADMastar.sh
qsub -l big cmp_bwavesgcccactusADMmilc.sh
qsub -l big cmp_bwavesgcccactusADMgromacs.sh
qsub -l big cmp_bwavesgccmcfhmmer.sh
qsub -l big cmp_bwavesgccmcfleslie3d.sh
