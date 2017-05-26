#!/bin/sh
# Job name
#$ -N pinned_splashwater.sp
# Shell
#$ -S /bin/bash

mkdir data.$JOB_ID
cd data.$JOB_ID
export GRAPHITE_ROOT=/scratch/nas/1/dn/sniper-6.0
export BENCHMARKS_ROOT=/scratch/nas/1/dn/sniper-6.0/benchmarks
ln -s /scratch/nas/1/dn/sniper-6.0/benchmarks sniper
./sniper/run-sniper -s mytrace:stats.out  --benchmarks=splash2-water.sp-large-1 -n 1 -c gainestown -c scheduler/small  -c scheduler/pinned  --sim-end=last-restart --power -d ~/data.$JOB_ID/result 
cd ~/data.$JOB_ID/result
mkdir /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/baseline_smallCore/$JOB_NAME
mv sim.* /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/baseline_smallCore/$JOB_NAME
mv power.* /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/baseline_smallCore/$JOB_NAME
mv stats.out /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/baseline_smallCore/$JOB_NAME
cd
mv $JOB_NAME.o$JOB_ID /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/baseline_smallCore/$JOB_NAME.o$JOB_ID
mv $JOB_NAME.e$JOB_ID /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/baseline_smallCore/$JOB_NAME.e$JOB_ID
rm -r data.$JOB_ID