#!/bin/sh
# Job name
#$ -N EightThreads_bwaves
# Shell
#$ -S /bin/bash

#mkdir data.$JOB_ID
#cd data.$JOB_ID
export GRAPHITE_ROOT=/scratch/nas/1/dn/sniper-6.0
export BENCHMARKS_ROOT=/scratch/nas/1/dn/sniper-6.0/benchmarks
ln -s /scratch/nas/1/dn/sniper-6.0 sniper
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/bwaves2/bwaves.0.sift bwaves.0.sift
#cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/2/.0.sift .0.sift
./sniper/run-sniper -s mytrace:stats.out -n 4 -c gainestown -c scheduler/big,scheduler/small,scheduler/small,scheduler/small -g --scheduler/type=big_small -g --scheduler/pinned/big_small=1000000 -s demorr_pinned.py --sim-end=last-restart --power -d ~/data.$JOB_ID/result --traces=bwaves.0.sift,bwaves.0.sift,bwaves.0.sift,bwaves.0.sift,bwaves.0.sift,bwaves.0.sift,bwaves.0.sift,bwaves.0.sift
cd ~/data.$JOB_ID/result
mkdir /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/_bigLittle_hrrs_spec_tugberk_rr/$JOB_NAME
mv sim.* /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/_bigLittle_hrrs_spec_tugberk_rr/$JOB_NAME
mv power.* /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/_bigLittle_hrrs_spec_tugberk_rr/$JOB_NAME
mv stats.out /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/_bigLittle_hrrs_spec_tugberk_rr/$JOB_NAME
cd
mv $JOB_NAME.o$JOB_ID /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/_bigLittle_hrrs_spec_tugberk_rr/$JOB_NAME.o$JOB_ID
mv $JOB_NAME.e$JOB_ID /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/_bigLittle_hrrs_spec_tugberk_rr/$JOB_NAME.e$JOB_ID
rm -r data.$JOB_ID