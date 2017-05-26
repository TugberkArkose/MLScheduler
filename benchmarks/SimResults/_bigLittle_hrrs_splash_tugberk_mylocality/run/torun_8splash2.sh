#!/bin/sh
qsub -l big EightThreads_barnes.sh
qsub -l big EightThreads_cholesky.sh
qsub -l big EightThreads_fft.sh
qsub -l big EightThreads_fmm.sh
qsub -l big EightThreads_lu.cont.sh
qsub -l big EightThreads_lu.ncont.sh
qsub -l big EightThreads_ocean.cont.sh
qsub -l big EightThreads_ocean.ncont.sh
qsub -l big EightThreads_radiosity.sh
qsub -l big EightThreads_radix.sh
qsub -l big EightThreads_raytrace.sh
qsub -l big EightThreads_water.nsq.sh
qsub -l big EightThreads_water.sp.sh
