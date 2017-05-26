#!/bin/sh
qsub -l big pinned_splashbarnes.sh
qsub -l big pinned_splashcholesky.sh
qsub -l big pinned_splashfft.sh
qsub -l big pinned_splashfmm.sh
qsub -l big pinned_splashlu.cont.sh
qsub -l big pinned_splashlu.ncont.sh
qsub -l big pinned_splashocean.cont.sh
qsub -l big pinned_splashocean.ncont.sh
qsub -l big pinned_splashradiosity.sh
qsub -l big pinned_splashradix.sh
qsub -l big pinned_splashraytrace.sh
qsub -l big pinned_splashwater.nsq.sh
qsub -l big pinned_splashwater.sp.sh
