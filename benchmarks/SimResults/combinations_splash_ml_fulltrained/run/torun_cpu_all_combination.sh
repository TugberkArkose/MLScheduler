#!/bin/sh
qsub -l big cmp_choleskybarnesfftfmm.sh
qsub -l big cmp_choleskybarnesfftocean.cont.sh
qsub -l big cmp_choleskybarnesfftraytrace.sh
qsub -l big cmp_choleskybarnesfftwater.sp.sh
qsub -l big cmp_choleskybarnesradiositylu.cont.sh
qsub -l big cmp_choleskybarnesradiosityocean.ncont.sh
