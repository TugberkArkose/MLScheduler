template = '''
# Job name
#$ -N %(hd)s%(label)s%(a)s%(b)s%(c)s
# Shell
#$ -S /bin/bash

mkdir %(DATA)s
cd data.$JOB_ID
export GRAPHITE_ROOT=%(CSCRATCHS)s
export BENCHMARKS_ROOT=%(CSCRATCH)s
ln -s %(CSCRATCHS)s sniper
cp %(CSCRATCH)s/SimResults/cpu_trace/%(a)s2/%(a)s.0.sift %(a)s.0.sift
cp %(CSCRATCH)s/SimResults/cpu_trace/%(label)s2/%(label)s.0.sift %(label)s.0.sift
cp %(CSCRATCH)s/SimResults/cpu_trace/%(b)s2/%(b)s.0.sift %(b)s.0.sift
cp %(CSCRATCH)s/SimResults/cpu_trace/%(c)s2/%(c)s.0.sift %(c)s.0.sift
./sniper/run-sniper -s mytrace:stats.out -n 4 -c gainestown -c scheduler/big,scheduler/small,scheduler/small,scheduler/small -g --scheduler/type=pinned -g --scheduler/pinned/quantum=1000000 -s demorr_pinned.py --sim-end=last-restart --power -d ~/data.$JOB_ID/result --traces=%(label)s.0.sift,%(b)s.0.sift,%(c)s.0.sift,%(a)s.0.sift
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

#torun = '#!/bin/sh\n'
torun = ''
#hd = 'multi_'

cpu_apps = ['gcc', 'bwaves', 'cactusADM', 'soplex', 'hmmer', 'astar', 'mcf', 'milc', 'zeusmp', 'gromacs', 'leslie3d']
apps = [['bwaves', 'GemsFDTD', 'astar', 'omnetpp'], ['soplex', 'mcf', 'calculix', 'gcc'], ['perlbench', 'gamess', 'bzip2', 'calculix'], ['astar', 'lbm', 'tonto', 'h264ref'], ['namd', 'gromacs', 'calculix', 'cactusADM'], ['zeusmp', 'xalancbmk', 'namd', 'gobmk'], ['sjeng', 'povray', 'omnetpp', 'milc'], ['calculix', 'libquantum', 'zeusmp', 'sjeng'], ['sjeng', 'leslie3d', 'gobmk', 'milc'], ['astar', 'zeusmp', 'cactusADM', 'GemsFDTD'], ['povray', 'gromacs', 'libquantum', 'bzip2']]

for [CSCRATCHS, CSCRATCH, DATA, v] in [['/scratch/nas/1/dn/sniper-6.0', '/scratch/nas/1/dn/sniper-6.0/benchmarks', 'data.$JOB_ID', 'micro_pinned_train_combos_RobSim']]:
  for i in cpu_apps:
    del cpu_apps[cpu_apps.index(i)]
    for j in cpu_apps:
      del cpu_apps[cpu_apps.index(j)]
      for k in cpu_apps:
        del cpu_apps[cpu_apps.index(k)]
        for t in cpu_apps:
          del cpu_apps[cpu_apps.index(t)]
          for [ext, hd, sch, script,label] in [['1','cmpD_','scheduler/pinned', '',j]]:
            f = open('%(hd)s%(label)s%(a)s%(b)s%(c)s.sh'%{'hd':hd,'label':label, 'a':i, 'b':k, 'c':t}, 'w')
            f.write(template %{'hd':hd,'label':label, 'a':i,'b':k,'c':t, 'sch':sch, 'script':script, 'ext':ext, 'CSCRATCHS':CSCRATCHS, 'CSCRATCH':CSCRATCH, 'DATA':DATA, 'v':v})
            f.close()
            torun += 'qsub -l big %(hd)s%(label)s%(a)s%(b)s%(c)s.sh\n'%{'hd':hd,'label':label, 'a':i, 'b':k, 'c':t}
            array += '%(label)s%(a)s%(b)s%(c)s '%{'a':i, 'label':label, 'b':k, 'c':t }
            #f = open('torun_cpu_all_combination.sh', 'a+')
	    #for item in torun:
            #    f.write(item)
            #f.write(torun)
            #f.close()
            f = open('getexetime.sh', 'w')
            f.write(getexe % {'array':array})
            f.close()
  for [ext, hd, sch, script] in [['1','cmpD_','scheduler/pinned', '']]:
    for i in apps:
      f = open('%(hd)s%(label)s%(a)s%(b)s%(c)s.sh'%{'hd':hd,'label':i[0], 'a':i[1], 'b':i[2], 'c':i[3]}, 'w')
      f.write(template %{'hd':hd,'label':i[0], 'a':i[1],'b':i[2],'c':i[3], 'sch':sch, 'script':script, 'ext':ext, 'CSCRATCHS':CSCRATCHS, 'CSCRATCH':CSCRATCH, 'DATA':DATA, 'v':v})
      f.close()
      torun += 'qsub -l big %(hd)s%(label)s%(a)s%(b)s%(c)s.sh\n'%{ 'hd':hd,'label':i[0], 'a':i[1], 'b':i[2], 'c':i[3] }
      array += '%(label)s%(a)s%(b)s%(c)s '%{'label':i[0], 'a':i[1], 'b':i[2], 'c':i[3]}
      #f = open('torun_cpu_all_combinationBB.sh', 'w')
      #f.write(torun)
      #f.close()
      f = open('getexetime.sh', 'w')
      f.write(getexe % {'array':array})
      f.close()
    f = open('torun_cpu_all_combination.sh', 'a')
    f.write(torun)
    f.close()

