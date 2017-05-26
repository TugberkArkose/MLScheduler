import random
from random import randrange

template = '''#!/bin/sh
# Job name
#$ -N %(hd)s%(label)s%(a)s
# Shell
#$ -S /bin/bash

#mkdir %(DATA)s
#cd data.$JOB_ID
export GRAPHITE_ROOT=%(CSCRATCHS)s
export BENCHMARKS_ROOT=%(CSCRATCH)s
ln -s %(CSCRATCHS)s sniper
cp %(CSCRATCH)s/SimResults/cpu_trace/%(a)s2/%(a)s.0.sift %(a)s.0.sift
#cp %(CSCRATCH)s/SimResults/cpu_trace/%(label)s2/%(label)s.0.sift %(label)s.0.sift
./sniper/run-sniper -s mytrace:stats.out -n 4 -c gainestown -c scheduler/big,scheduler/small,scheduler/small,scheduler/small -g --scheduler/type=big_small -g --scheduler/pinned/big_small=1000000 -s demorr_pinned.py --sim-end=last-restart --power -d ~/data.$JOB_ID/result --traces=%(a)s.0.sift,%(a)s.0.sift,%(a)s.0.sift,%(a)s.0.sift,%(a)s.0.sift,%(a)s.0.sift,%(a)s.0.sift,%(a)s.0.sift
cd ~/data.$JOB_ID/result
mkdir %(CSCRATCH)s/SimResults/%(v)s/$JOB_NAME
mv sim.* %(CSCRATCH)s/SimResults/%(v)s/$JOB_NAME
mv power.* %(CSCRATCH)s/SimResults/%(v)s/$JOB_NAME
mv stats.out %(CSCRATCH)s/SimResults/%(v)s/$JOB_NAME
cd
mv $JOB_NAME.o$JOB_ID %(CSCRATCH)s/SimResults/%(v)s/$JOB_NAME.o$JOB_ID
mv $JOB_NAME.e$JOB_ID %(CSCRATCH)s/SimResults/%(v)s/$JOB_NAME.e$JOB_ID
rm -r %(DATA)s'''
getexe = '''#!/bin/bash
for p in pinned fair tlss hrrs;
do
  echo $p;
  for i in %(array)s;
  do
    var=$(cat $p$i/sim.out | grep Time | tr '|' '\\n' | tail -4 | sort -n | tail -1) ;
    echo $i $var;
  done
done'''
array = ''

torun = '#!/bin/sh\n'
#hd = 'multi_'

cpu_apps = ['perlbench', 'bzip2', 'gcc', 'bwaves', 'gamess', 'mcf', 'milc', 'zeusmp', 'gromacs', 'cactusADM', 'leslie3d', 'namd', 'gobmk', 'soplex', 'povray', 'calculix', 'hmmer', 'sjeng', 'GemsFDTD', 'libquantum', 'h264ref', 'tonto', 'lbm', 'omnetpp', 'astar', 'xalancbmk']
min_cpu_apps = ['perlbench', 'bzip2', 'gcc', 'bwaves', 'gamess', 'mcf', 'milc', 'zeusmp', 'gromacs', 'cactusADM', 'leslie3d', 'namd', 'gobmk', 'soplex', 'povray', 'calculix', 'hmmer', 'sjeng', 'GemsFDTD', 'libquantum', 'h264ref', 'tonto', 'lbm', 'omnetpp', 'astar', 'xalancbmk']

for [CSCRATCHS, CSCRATCH, DATA, v] in [['/scratch/nas/1/dn/sniper-6.0', '/scratch/nas/1/dn/sniper-6.0/benchmarks', 'data.$JOB_ID', '_bigLittle_hrrs_spec_tugberk_rr']]:
  for i in cpu_apps:
    del min_cpu_apps[0]
    #for j in min_cpu_apps:
    for [ext, hd, sch, script,label] in [['1','EightThreads_','scheduler/hrrs', '','']]:
      f = open('%(hd)s%(label)s%(a)s8.sh'%{'hd':hd,'label':label, 'a':i}, 'w')
      f.write(template %{'hd':hd,'label':label, 'a':i, 'sch':sch, 'script':script, 'ext':ext, 'CSCRATCHS':CSCRATCHS, 'CSCRATCH':CSCRATCH, 'DATA':DATA, 'v':v})
      f.close()
      torun += 'qsub -l big %(hd)s%(label)s%(a)s8.sh\n'%{'hd':hd,'label':label, 'a':i}
    array += '%(a)s '%{'a':i}
  f = open('torun_cpu8.sh', 'w')
  f.write(torun)
  f.close()
  f = open('getexetime.sh', 'w')
  f.write(getexe % {'array':array})
  f.close()
