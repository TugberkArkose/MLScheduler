#!/bin/sh
# Job name
#$ -N pinned_splashocean.cont
# Shell
#$ -S /bin/bash

mkdir data.$JOB_ID
cd data.$JOB_ID
export GRAPHITE_ROOT=/scratch/nas/1/dn/sniper-6.0
export BENCHMARKS_ROOT=/scratch/nas/1/dn/sniper-6.0/benchmarks
ln -s /scratch/nas/1/dn/sniper-6.0/benchmarks sniper
./sniper/run-sniper -s mytrace:stats.out  --benchmarks=splash2-ocean.cont-large-1 -n 1 -c gainestown -c scheduler/big  -c scheduler/pinned  --sim-end=last-restart --power -d ~/data.$JOB_ID/result 
cd ~/data.$JOB_ID/result
mkdir /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/baseline_bigCore/$JOB_NAME
mv sim.* /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/baseline_bigCore/$JOB_NAME
mv power.* /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/baseline_bigCore/$JOB_NAME
mv stats.out /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/baseline_bigCore/$JOB_NAME
cd
mv $JOB_NAME.o$JOB_ID /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/baseline_bigCore/$JOB_NAME.o$JOB_ID
mv $JOB_NAME.e$JOB_ID /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/baseline_bigCore/$JOB_NAME.e$JOB_ID
rm -r data.$JOB_ID