#!/bin/sh
# Job name
#$ -N EightThreads_ocean.ncont
# Shell
#$ -S /bin/bash

mkdir data.$JOB_ID
cd data.$JOB_ID
export GRAPHITE_ROOT=/scratch/nas/1/dn/sniper-6.0
export BENCHMARKS_ROOT=/scratch/nas/1/dn/sniper-6.0/benchmarks
ln -s /scratch/nas/1/dn/sniper-6.0/benchmarks sniper
./sniper/run-sniper -s mytrace:stats.out -g --scheduler/type=pinned -g --scheduler/pinned/quantum=1000000 --benchmarks=splash2-ocean.ncont-large-1,splash2-ocean.ncont-large-1,splash2-ocean.ncont-large-1,splash2-ocean.ncont-large-1,splash2-ocean.ncont-large-1,splash2-ocean.ncont-large-1,splash2-ocean.ncont-large-1,splash2-ocean.ncont-large-1 -n 4 -c gainestown -c scheduler/big,scheduler/small,scheduler/small,scheduler/small -s demorr_pinned.py --sim-end=last-restart --power -d ~/data.$JOB_ID/result 
cd ~/data.$JOB_ID/result
mkdir /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/_bigLittle_hrrs_splash_tugberk_pinned/$JOB_NAME
mv sim.* /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/_bigLittle_hrrs_splash_tugberk_pinned/$JOB_NAME
mv power.* /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/_bigLittle_hrrs_splash_tugberk_pinned/$JOB_NAME
mv stats.out /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/_bigLittle_hrrs_splash_tugberk_pinned/$JOB_NAME
cd
mv $JOB_NAME.o$JOB_ID /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/_bigLittle_hrrs_splash_tugberk_pinned/$JOB_NAME.o$JOB_ID
mv $JOB_NAME.e$JOB_ID /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/_bigLittle_hrrs_splash_tugberk_pinned/$JOB_NAME.e$JOB_ID
rm -r data.$JOB_ID