# Job name
#$ -N rr_ml
# Shell
#$ -S /bin/bash

mkdir data.$JOB_ID
cd data.$JOB_ID

export GRAPHITE_ROOT=/scratch/nas/1/dn/sniper-6.0
export BENCHMARKS_ROOT=/scratch/nas/1/dn/sniper-6.0/benchmarks
CURRENT_ENVIRONMENT=/scratch/nas/1/dn/scikit_learn_latest
source $CURRENT_ENVIRONMENT/bin/activate

ln -s /scratch/nas/1/dn/sniper-6.0 sniper

cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/perlbench2/perlbench.0.sift perlbench.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/bzip22/bzip2.0.sift bzip2.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/gcc2/gcc.0.sift gcc.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/bwaves2/bwaves.0.sift bwaves.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/gamess2/gamess.0.sift gamess.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/mcf2/mcf.0.sift mcf.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/milc2/milc.0.sift milc.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/zeusmp2/zeusmp.0.sift zeusmp.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/gromacs2/gromacs.0.sift gromacs.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/cactusADM2/cactusADM.0.sift cactusADM.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/leslie3d2/leslie3d.0.sift leslie3d.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/namd2/namd.0.sift namd.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/gobmk2/gobmk.0.sift gobmk.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/soplex2/soplex.0.sift soplex.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/povray2/povray.0.sift povray.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/calculix2/calculix.0.sift calculix.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/hmmer2/hmmer.0.sift hmmer.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/sjeng2/sjeng.0.sift sjeng.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/GemsFDTD2/GemsFDTD.0.sift GemsFDTD.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/libquantum2/libquantum.0.sift libquantum.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/h264ref2/h264ref.0.sift h264ref.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/tonto2/tonto.0.sift tonto.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/lbm2/lbm.0.sift lbm.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/omnetpp2/omnetpp.0.sift omnetpp.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/astar2/astar.0.sift astar.0.sift
cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/xalancbmk2/xalancbmk.0.sift xalancbmk.0.sift

#cp /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/cpu_trace/2/.0.sift .0.sift
./sniper/run-sniper -s mytrace:stats.out -n 4 -c gainestown -c scheduler/big,scheduler/small,scheduler/small,scheduler/small -g --scheduler/type=pinned -g --scheduler/pinned/quantum=1000000 -s newSchedulerRoundRobinBased.py --sim-end=last --power -d ~/data.$JOB_ID/result --traces=perlbench.0.sift,bzip2.0.sift,gcc.0.sift,bwaves.0.sift,gamess.0.sift,mcf.0.sift,milc.0.sift,zeusmp.0.sift,gromacs.0.sift,cactusADM.0.sift,leslie3d.0.sift,namd.0.sift,gobmk.0.sift,soplex.0.sift,povray.0.sift,calculix.0.sift,hmmer.0.sift,sjeng.0.sift,GemsFDTD.0.sift,libquantum.0.sift,h264ref.0.sift,tonto.0.sift,lbm.0.sift,omnetpp.0.sift,astar.0.sift,xalancbmk.0.sift


cd ~/data.$JOB_ID/result
mkdir /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/Paper2_rr_spec_ml/$JOB_NAME
mv sim.* /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/Paper2_rr_spec_ml/$JOB_NAME
mv power.* /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/Paper2_rr_spec_ml/$JOB_NAME
mv stats.out /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/Paper2_rr_spec_ml/$JOB_NAME
cd
mv $JOB_NAME.o$JOB_ID /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/Paper2_rr_spec_ml/$JOB_NAME.o$JOB_ID
mv $JOB_NAME.e$JOB_ID /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/Paper2_rr_spec_ml/$JOB_NAME.e$JOB_ID


