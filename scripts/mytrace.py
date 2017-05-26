"""
ipctrace.py

Write a trace of instantaneous IPC values for all cores.
First argument is either a filename, or none to write to standard output.
Second argument is the interval size in nanoseconds (default is 10000)
"""

import sys, os, sim

class myTrace:
  def setup(self, args):
    args = dict(enumerate((args or '').split(':')))
    filename = args.get(0, None)
    interval_ns = long(args.get(1, 1000000))
    if filename:
      self.fd = file(os.path.join(sim.config.output_dir, filename), 'w')
      self.isTerminal = False
    else:
      self.fd = sys.stdout
      self.isTerminal = True
    self.sd = sim.util.StatsDelta()
    self.stats = {
      'time': [ self.getStatsGetter('performance_model', core, 'elapsed_time') for core in range(sim.config.ncores) ],
      'ffwd_time': [ self.getStatsGetter('fastforward_performance_model', core, 'fastforwarded_time') for core in range(sim.config.ncores) ],
      'instrs': [ self.getStatsGetter('performance_model', core, 'instruction_count') for core in range(sim.config.ncores) ],
      'coreinstrs': [ self.getStatsGetter('core', core, 'instructions') for core in range(sim.config.ncores) ],
      'brhits': [ self.getStatsGetter('branch_predictor', core, 'num-correct') for core in range(sim.config.ncores) ],
      'brmisses': [ self.getStatsGetter('branch_predictor', core, 'num-incorrect') for core in range(sim.config.ncores) ],
      'dramreqs': [ self.getStatsGetter('dram-queue', core, 'num-requests') for core in range(sim.config.ncores) ],
      'dramreads': [ self.getStatsGetter('dram', core, 'reads') for core in range(sim.config.ncores) ],
      'dramwrites': [ self.getStatsGetter('dram', core, 'writes') for core in range(sim.config.ncores) ],
      'dtlbaccess': [ self.getStatsGetter('dtlb', core, 'access') for core in range(sim.config.ncores) ],
      'dtlbmisses': [ self.getStatsGetter('dtlb', core, 'miss') for core in range(sim.config.ncores) ],
      'itlbaccess': [ self.getStatsGetter('itlb', core, 'access') for core in range(sim.config.ncores) ],
      'itlbmisses': [ self.getStatsGetter('itlb', core, 'miss') for core in range(sim.config.ncores) ],  
      'stlbaccess': [ self.getStatsGetter('stlb', core, 'access') for core in range(sim.config.ncores) ],
      'stlbmisses': [ self.getStatsGetter('stlb', core, 'miss') for core in range(sim.config.ncores) ],
      'dl1loads': [ self.getStatsGetter('L1-D', core, 'loads') for core in range(sim.config.ncores) ],
      'dl1misses': [ self.getStatsGetter('L1-D', core, 'load-misses') for core in range(sim.config.ncores) ],
      'dl1stores': [ self.getStatsGetter('L1-D', core, 'stores') for core in range(sim.config.ncores) ],
      'il1loads': [ self.getStatsGetter('L1-I', core, 'loads') for core in range(sim.config.ncores) ],
      'il1misses': [ self.getStatsGetter('L1-I', core, 'load-misses') for core in range(sim.config.ncores) ],
      'il1stores': [ self.getStatsGetter('L1-I', core, 'stores') for core in range(sim.config.ncores) ],
      'l2loads': [ self.getStatsGetter('L2', core, 'loads') for core in range(sim.config.ncores) ],
      'l2misses': [ self.getStatsGetter('L2', core, 'load-misses') for core in range(sim.config.ncores) ],
      'l2stores': [ self.getStatsGetter('L2', core, 'stores') for core in range(sim.config.ncores) ],
      'l3loads': [ self.getStatsGetter('L3', core, 'loads') for core in range(sim.config.ncores) ],
      'l3misses': [ self.getStatsGetter('L3', core, 'load-misses') for core in range(sim.config.ncores) ],
      'l3stores': [ self.getStatsGetter('L3', core, 'stores') for core in range(sim.config.ncores) ],
      'uopbr': [ self.getStatsGetter('interval_timer', core, 'uop_branch') for core in range(sim.config.ncores) ],
      'uopfpaddsub': [ self.getStatsGetter('interval_timer', core, 'uop_fp_addsub') for core in range(sim.config.ncores) ],
      'uopfpmuldiv': [ self.getStatsGetter('interval_timer', core, 'uop_fp_muldiv') for core in range(sim.config.ncores) ],
      'uopgeneric': [ self.getStatsGetter('interval_timer', core, 'uop_generic') for core in range(sim.config.ncores) ],
      'uopld': [ self.getStatsGetter('interval_timer', core, 'uop_load') for core in range(sim.config.ncores) ],
      'uopst': [ self.getStatsGetter('interval_timer', core, 'uop_store') for core in range(sim.config.ncores) ],
      'uoptotal': [ self.getStatsGetter('interval_timer', core, 'uops_total') for core in range(sim.config.ncores) ],

    }
    sim.util.Every(interval_ns * sim.util.Time.NS, self.periodic, statsdelta = self.sd, roi_only = True)

  def periodic(self, time, time_delta):
    if self.isTerminal:
      self.fd.write('[IPC] [BRhits] [BRmiss] [DRAMreq] [DRAMrd] [DRAMwr] [DTLBacc] [DTLBmiss] [ITLBacc] [ITLBmiss] [STLBacc] [STLBmiss] [DL1ld] [DL1miss] [DL1st] [IL1ld] [IL1miss] [IL1st] [L2ld] [L2miss] [L2st] [L3ld] [L3miss] [L3st] [uopBR] [uopFPaddsub] [uopFPmuldiv] [uopGeneric] [uopLD] [uopST] [uopTotal] ')
    self.fd.write('%u' % (time / 1e6)) # Time in ns
    for core in range(sim.config.ncores):
      # detailed-only IPC
      cycles = (self.stats['time'][core].delta - self.stats['ffwd_time'][core].delta) * sim.dvfs.get_frequency(core) / 1e9 # convert fs to cycles
      instrs = self.stats['instrs'][core].delta
      ipc = instrs / (cycles or 1) # Avoid division by zero
      #self.fd.write(' %.3f' % ipc)

      # include fast-forward IPCs
      cycles = self.stats['time'][core].delta * sim.dvfs.get_frequency(core) / 1e9 # convert fs to cycles
      instrs = self.stats['coreinstrs'][core].delta
      ipc = instrs / (cycles or 1)
      self.fd.write(' %.3f' % ipc)

      temp = self.stats['brhits'][core].delta
      self.fd.write(' %.3f' % temp)
      tmp = self.stats['brmisses'][core].delta
      self.fd.write(' %.3f' % tmp)
      temp = self.stats['dramreqs'][core].delta
      self.fd.write(' %.3f' % temp)
      tmp = self.stats['dramreads'][core].delta
      self.fd.write(' %.3f' % tmp)
      temp = self.stats['dramwrites'][core].delta
      self.fd.write(' %.3f' % temp)
      tmp = self.stats['dtlbaccess'][core].delta
      self.fd.write(' %.3f' % tmp)
      temp = self.stats['dtlbmisses'][core].delta
      self.fd.write(' %.3f' % temp)
      tmp = self.stats['itlbaccess'][core].delta
      self.fd.write(' %.3f' % tmp)
      temp = self.stats['itlbmisses'][core].delta
      self.fd.write(' %.3f' % temp)
      tmp = self.stats['stlbaccess'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['stlbmisses'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['dl1loads'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['dl1misses'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['dl1stores'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['il1loads'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['il1misses'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['il1stores'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['l2loads'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['l2misses'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['l2stores'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['l3loads'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['l3misses'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['l3stores'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['uopbr'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['uopfpaddsub'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['uopfpmuldiv'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['uopgeneric'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['uopld'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['uopst'][core].delta
      self.fd.write(' %.3f' % tmp)
      tmp = self.stats['uoptotal'][core].delta
      self.fd.write(' %.3f' % tmp)


      self.fd.write('\n')

  def getStatsGetter(self, component, core, metric):
    # Some components don't exist (i.e. DRAM reads on cores that don't have a DRAM controller),
    # return a special object that always returns 0 in these cases
    try:
      return self.sd.getter(component, core, metric)
    except:
      class Zero():
        def __init__(self): self.delta = 0
        def update(self): pass
      return Zero()

sim.util.register(myTrace())
