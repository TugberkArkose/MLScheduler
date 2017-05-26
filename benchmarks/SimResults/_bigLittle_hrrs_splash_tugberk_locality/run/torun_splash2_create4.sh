#!/bin/sh
qsub -l big cmp_barnes.sh
qsub -l big cmp_cholesky.sh
qsub -l big cmp_fft.sh
qsub -l big cmp_fmm.sh
qsub -l big cmp_lu.cont.sh
qsub -l big cmp_lu.ncont.sh
qsub -l big cmp_ocean.cont.sh
qsub -l big cmp_ocean.ncont.sh
qsub -l big cmp_radiosity.sh
qsub -l big cmp_radix.sh
qsub -l big cmp_raytrace.sh
qsub -l big cmp_water.nsq.sh
qsub -l big cmp_water.sp.sh
