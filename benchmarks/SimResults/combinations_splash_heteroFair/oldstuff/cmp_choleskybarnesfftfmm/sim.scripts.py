import sys
sys.argv = [ "/scratch/nas/1/dn/sniper-6.0/scripts/mytrace.py", "stats.out" ]
execfile("/scratch/nas/1/dn/sniper-6.0/scripts/mytrace.py")
sys.argv = [ "/scratch/nas/1/dn/sniper-6.0/scripts/scheduler-heteroFair.py", "" ]
execfile("/scratch/nas/1/dn/sniper-6.0/scripts/scheduler-heteroFair.py")
