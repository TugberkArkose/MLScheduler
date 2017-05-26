import random
from random import randrange

template = '''#!/bin/sh
# Job name
#$ -N %(label)s%(a)s
# Shell
#$ -S /bin/bash

mkdir %(DATA)s
cd data.$JOB_ID
export GRAPHITE_ROOT=%(CSCRATCHS)s
export BENCHMARKS_ROOT=%(CSCRATCH)s
ln -s %(CSCRATCH)s sniper
./sniper/run-sniper -s mytrace:stats.out  --benchmarks=splash2-%(a)s-large-%(ext)s -n 1 -c gainestown -c scheduler/big  -c %(sch)s %(script)s --sim-end=last-restart --power -d ~/data.$JOB_ID/result 
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

#cpu_apps = ['perlbench', 'bzip2', 'gcc', 'bwaves', 'gamess', 'mcf', 'milc', 'zeusmp', 'gromacs', 'cactusADM', 'leslie3d', 'namd', 'gobmk', 'soplex', 'povray', 'calculix', 'hmmer', 'sjeng', 'GemsFDTD', 'libquantum', 'h264ref', 'tonto', 'lbm', 'omnetpp', 'astar', 'wrf', 'sphinx3', 'xalancbmk']
for [CSCRATCHS, CSCRATCH, DATA, v] in [['/scratch/nas/1/dn/sniper-6.0', '/scratch/nas/1/dn/sniper-6.0/benchmarks', 'data.$JOB_ID', 'baseline_bigCore']]:
  for i in splash2_apps:
    for [ext] in [['1']]:
      for [sch, script, label] in [['scheduler/pinned', '', 'pinned_splash']]:
        f = open('%(label)s%(a)s.sh'%{'label':label, 'a':i}, 'w')
        f.write(template % {'label':label, 'a':i, 'sch':sch, 'script':script, 'ext':ext, 'CSCRATCHS':CSCRATCHS, 'CSCRATCH':CSCRATCH, 'DATA':DATA, 'v':v})
        f.close()
        torun += 'qsub -l big %(label)s%(a)s.sh\n'%{'label':label, 'a':i}
      array += '%(a)s '%{'a':i}
  f = open('torun_splash2.sh', 'w')
  f.write(torun)
  f.close()
  f = open('getexetime.sh', 'w')
  f.write(getexe % {'array':array})
  f.close()



      #for [sch, script, label] in [['scheduler/pinned', '', 'pinned'], ['scheduler/pinned', '-s scheduler-mylocality:4000000:equal_time', 'fair'], ['scheduler/hrrs', '', 'hrrs']]:
#
