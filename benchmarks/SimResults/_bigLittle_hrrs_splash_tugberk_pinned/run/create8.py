import random
from random import randrange

template = '''#!/bin/sh
# Job name
#$ -N %(hd)s%(label)s%(a)s
# Shell
#$ -S /bin/bash

mkdir %(DATA)s
cd data.$JOB_ID
export GRAPHITE_ROOT=%(CSCRATCHS)s
export BENCHMARKS_ROOT=%(CSCRATCH)s
ln -s %(CSCRATCH)s sniper
./sniper/run-sniper -s mytrace:stats.out -g --scheduler/type=pinned -g --scheduler/pinned/quantum=1000000 --benchmarks=splash2-%(a)s-large-%(ext)s,splash2-%(a)s-large-%(ext)s,splash2-%(a)s-large-%(ext)s,splash2-%(a)s-large-%(ext)s,splash2-%(a)s-large-%(ext)s,splash2-%(a)s-large-%(ext)s,splash2-%(a)s-large-%(ext)s,splash2-%(a)s-large-%(ext)s -n 4 -c gainestown -c scheduler/big,scheduler/small,scheduler/small,scheduler/small -s demorr_pinned.py --sim-end=last-restart --power -d ~/data.$JOB_ID/result 
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
for p in pinned fair hrrs tlss;
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
splash2_apps = ['barnes', 'cholesky', 'fft', 'fmm', 'lu.cont', 'lu.ncont', 'ocean.cont', 'ocean.ncont', 'radiosity', 'radix', 'raytrace', 'water.nsq', 'water.sp']
min_splash_apps = ['barnes', 'cholesky', 'fft', 'fmm', 'lu.cont', 'lu.ncont', 'ocean.cont', 'ocean.ncont', 'radiosity', 'radix', 'raytrace', 'water.nsq', 'water.sp']
#cpu_apps = ['perlbench', 'bzip2', 'gcc', 'bwaves', 'gamess', 'mcf', 'milc', 'zeusmp', 'gromacs', 'cactusADM', 'leslie3d', 'namd', 'gobmk', 'soplex', 'povray', 'calculix', 'hmmer', 'sjeng', 'GemsFDTD', 'libquantum', 'h264ref', 'tonto', 'lbm', 'omnetpp', 'astar', 'wrf', 'sphinx3', 'xalancbmk']
for [CSCRATCHS, CSCRATCH, DATA, v] in [['/scratch/nas/1/dn/sniper-6.0', '/scratch/nas/1/dn/sniper-6.0/benchmarks', 'data.$JOB_ID', '_bigLittle_hrrs_splash_tugberk_pinned']]:
  for i in splash2_apps:
    del min_splash_apps[0]
    #for j in min_splash_apps: 
    for [ext, sch, script, hd, label] in [['1','scheduler/pinned', '', 'EightThreads_','']]:
      f = open('%(hd)s%(label)s%(a)s.sh'%{'hd':hd, 'label':label, 'a':i}, 'w')
      f.write(template % {'hd':hd, 'label':label, 'a':i, 'sch':sch, 'script':script, 'ext':ext, 'CSCRATCHS':CSCRATCHS, 'CSCRATCH':CSCRATCH, 'DATA':DATA, 'v':v})
      f.close()
      torun += 'qsub -l big %(hd)s%(a)s.sh\n'%{'hd':hd, 'label':label, 'a':i}
    array += '%(a)s '%{'a':i}
  f = open('torun_splash28.sh', 'w')
  f.write(torun)
  f.close()
  f = open('getexetime.sh', 'w')
  f.write(getexe % {'array':array})
  f.close()



      #for [sch, script, label] in [['scheduler/pinned', '', 'pinned'], ['scheduler/pinned', '-s scheduler-mylocality:4000000:equal_time', 'fair'], ['scheduler/hrrs', '', 'hrrs']]:
#
