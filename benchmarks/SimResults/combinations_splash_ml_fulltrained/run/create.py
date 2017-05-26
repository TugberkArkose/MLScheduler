import random
from random import randrange

template = '''#!/bin/sh
# Job name
#$ -N %(hd)s%(label)s%(a)s%(b)s%(c)s
# Shell
#$ -S /bin/bash

mkdir %(DATA)s
cd data.$JOB_ID
export GRAPHITE_ROOT=%(CSCRATCHS)s
export BENCHMARKS_ROOT=%(CSCRATCH)s
ln -s %(CSCRATCH)s sniper
./sniper/run-sniper -s mytrace:stats.out -s MLScheduler_fulltrained.py -g --scheduler/type=pinned -g --scheduler/pinned/quantum=1000000 --benchmarks=splash2-%(a)s-large-%(ext)s,splash2-%(label)s-large-%(ext)s,splash2-%(b)s-large-%(ext)s,splash2-%(c)s-large-%(ext)s -n 4 -c gainestown -c scheduler/big,scheduler/small,scheduler/small,scheduler/small --sim-end=last-restart --power -d ~/data.$JOB_ID/result
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
#min_splash_apps = ['barnes', 'cholesky', 'fft', 'fmm', 'lu.cont', 'lu.ncont', 'ocean.cont', 'ocean.ncont', 'radiosity', 'radix', 'raytrace', 'water.nsq', 'water.sp']
splash_apps = ['barnes', 'cholesky', 'fft', 'fmm', 'lu.cont', 'ocean.cont', 'radiosity', 'raytrace', 'radix', 'water.sp', 'ocean.ncont']
#cpu_apps = ['perlbench', 'bzip2', 'gcc', 'bwaves', 'gamess', 'mcf', 'milc', 'zeusmp', 'gromacs', 'cactusADM', 'leslie3d', 'namd', 'gobmk', 'soplex', 'povray', 'calculix', 'hmmer', 'sjeng', 'GemsFDTD', 'libquantum', 'h264ref', 'tonto', 'lbm', 'omnetpp', 'astar', 'wrf', 'sphinx3', 'xalancbmk']
for [CSCRATCHS, CSCRATCH, DATA, v] in [['/scratch/nas/1/dn/sniper-6.0', '/scratch/nas/1/dn/sniper-6.0/benchmarks', 'data.$JOB_ID', 'combinations_splash_ml_fulltrained']]:
    for i in splash_apps:
      del splash_apps[splash_apps.index(i)]
      for j in splash_apps:
        del splash_apps[splash_apps.index(j)]
        for k in splash_apps:
          del splash_apps[splash_apps.index(k)]
          for t in splash_apps:
            del splash_apps[splash_apps.index(t)]
            for [ext, hd, sch, script,label] in [['1','cmp_','scheduler/pinned', '',j]]:
              f = open('%(hd)s%(label)s%(a)s%(b)s%(c)s.sh'%{'hd':hd,'label':label, 'a':i, 'b':k, 'c':t}, 'w')
              f.write(template %{'hd':hd,'label':label, 'a':i,'b':k,'c':t, 'sch':sch, 'script':script, 'ext':ext, 'CSCRATCHS':CSCRATCHS, 'CSCRATCH':CSCRATCH, 'DATA':DATA, 'v':v})
              f.close()
              torun += 'qsub -l big %(hd)s%(label)s%(a)s%(b)s%(c)s.sh\n'%{'hd':hd,'label':label, 'a':i, 'b':k, 'c':t}
              array += '%(label)s%(a)s%(b)s%(c)s '%{'a':i, 'label':label, 'b':k, 'c':t }
              f = open('torun_cpu_all_combination.sh', 'w')
              f.write(torun)
              f.close()
              f = open('getexetime.sh', 'w')
              f.write(getexe % {'array':array})
              f.close()



      #for [sch, script, label] in [['scheduler/pinned', '', 'pinned'], ['scheduler/pinned', '-s scheduler-mylocality:4000000:equal_time', 'fair'], ['scheduler/hrrs', '', 'hrrs']]:
#
