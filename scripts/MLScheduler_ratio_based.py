import os
import json
import itertools
import sim

BIG = [0]
SMALL = [1,2,3]
PATH = "python /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/myNumpy0401.py "
#PATH = "python /home/tugberk/Bsc/DaniThesis/myNumpy0401.py "
STATSORDER = ['brhits', 'brmisses', 'dramreqs', 'dramreads', 'dramwrites', 'dtlbaccess', 'dtlbmisses', 'itlbaccess', 'itlbmisses', 'stlbaccess',
    'stlbmisses', 'dl1loads', 'dl1misses', 'dl1stores', 'il1loads', 'il1misses', 'l2loads', 'l2misses', 'l2stores',
    'l3loads', 'l3misses', 'l3stores', 'uopbr', 'uopfpaddsub', 'uopfpmuldiv', 'uopgeneric', 'uopld', 'uopst', 'uoptotal']

def getScoreMetricTime(thread_id):
    return long(sim.stats.get('thread', thread_id, 'nonidle_elapsed_time'))

def getScoreMetricInstructions(thread_id):
    return long(sim.stats.get('thread', thread_id, 'instruction_count'))


class Thread:

    global BIG
    global SMALL
    global PATH
    global STATSORDER

    def __init__(self, thread_id):
        self.thread_id = thread_id
        self.core = None
        self.runnable = False
        self.unscheduled = False
        self.ipc = 0.1
        self.predicted_ipc = 0.1
        self.score = 0       # Accumulated score
        sim.thread.set_thread_affinity(self.thread_id, ())


    def updateScore(self, stats):
        cycles = stats['time'][self.core].delta * sim.dvfs.get_frequency(self.core) / 1e9  # convert fs to cycles
        instrs = stats['coreinstrs'][self.core].delta
        self.ipc = instrs / (cycles or 1)
        self.predicted_ipc = self.send_stats(stats)
        print self.core
        if self.core in BIG:
            self.score = self.ipc / self.predicted_ipc
        elif self.core in SMALL:
            self.score = self.predicted_ipc / self.ipc
        print self.score
        print self.thread_id


    def setScore(self, score):
        self.score = score

    def setCore(self, core_id, time = -1):
        self.core = core_id
        if core_id is None:
            self.last_scheduled_out = time
            sim.thread.set_thread_affinity(self.thread_id, ())
        else:
            self.last_scheduled_in = time
            sim.thread.set_thread_affinity(self.thread_id, [ c == core_id for c in range(sim.config.ncores) ])

    def send_stats(self, stats):

        statlist = []

        if self.core in BIG:
            statlist.append(self.ipc)
            for key in STATSORDER:
                statlist.append((stats[key])[self.core].delta)
            jlist = json.dumps(statlist, separators=(',', ':'))
            proc = os.popen(PATH + str(0) + " " + jlist).read()
            #result = json.loads(proc)
            #code above does not work check why
            result = proc
            fresult = float(result)
            return fresult

        if self.core in SMALL:
            statlist.append(self.ipc)
            for key in STATSORDER:
                statlist.append((stats[key])[self.core].delta)
            jlist = json.dumps(statlist, separators=(',', ':'))
            proc = os.popen(PATH +str(1)+ " " + jlist).read()
            #result = json.loads(proc)
            #code above does not work check why
            result = proc
            fresult = float(result)
            return fresult

    def __repr__(self):
        return 'Thread(%d,ipc = %f, %s, score = %f)' % (self.thread_id, self.ipc, 'core = %d' % self.core if self.core is not None else 'no core', self.score)


class SchedulerLocality:

    def setup(self, args):

        self.icount_last = [0 for core in range(sim.config.ncores)]
        self.last_reschedule = 0


        self.sd = sim.util.StatsDelta()
        self.stats = {
            'time': [self.getStatsGetter('performance_model', core, 'elapsed_time') for core in
                     range(sim.config.ncores)],
            'ffwd_time': [self.getStatsGetter('fastforward_performance_model', core, 'fastforwarded_time') for core in
                          range(sim.config.ncores)],
            'instrs': [self.getStatsGetter('performance_model', core, 'instruction_count') for core in
                       range(sim.config.ncores)],
            'coreinstrs': [self.getStatsGetter('core', core, 'instructions') for core in range(sim.config.ncores)],
            'brhits': [self.getStatsGetter('branch_predictor', core, 'num-correct') for core in
                       range(sim.config.ncores)],
            'brmisses': [self.getStatsGetter('branch_predictor', core, 'num-incorrect') for core in
                         range(sim.config.ncores)],
            'dramreqs': [self.getStatsGetter('dram-queue', core, 'num-requests') for core in range(sim.config.ncores)],
            'dramreads': [self.getStatsGetter('dram', core, 'reads') for core in range(sim.config.ncores)],
            'dramwrites': [self.getStatsGetter('dram', core, 'writes') for core in range(sim.config.ncores)],
            'dtlbaccess': [self.getStatsGetter('dtlb', core, 'access') for core in range(sim.config.ncores)],
            'dtlbmisses': [self.getStatsGetter('dtlb', core, 'miss') for core in range(sim.config.ncores)],
            'itlbaccess': [self.getStatsGetter('itlb', core, 'access') for core in range(sim.config.ncores)],
            'itlbmisses': [self.getStatsGetter('itlb', core, 'miss') for core in range(sim.config.ncores)],
            'stlbaccess': [self.getStatsGetter('stlb', core, 'access') for core in range(sim.config.ncores)],
            'stlbmisses': [self.getStatsGetter('stlb', core, 'miss') for core in range(sim.config.ncores)],
            'dl1loads': [self.getStatsGetter('L1-D', core, 'loads') for core in range(sim.config.ncores)],
            'dl1misses': [self.getStatsGetter('L1-D', core, 'load-misses') for core in range(sim.config.ncores)],
            'dl1stores': [self.getStatsGetter('L1-D', core, 'stores') for core in range(sim.config.ncores)],
            'il1loads': [self.getStatsGetter('L1-I', core, 'loads') for core in range(sim.config.ncores)],
            'il1misses': [self.getStatsGetter('L1-I', core, 'load-misses') for core in range(sim.config.ncores)],
            'l2loads': [self.getStatsGetter('L2', core, 'loads') for core in range(sim.config.ncores)],
            'l2misses': [self.getStatsGetter('L2', core, 'load-misses') for core in range(sim.config.ncores)],
            'l2stores': [self.getStatsGetter('L2', core, 'stores') for core in range(sim.config.ncores)],
            'l3loads': [self.getStatsGetter('L3', core, 'loads') for core in range(sim.config.ncores)],
            'l3misses': [self.getStatsGetter('L3', core, 'load-misses') for core in range(sim.config.ncores)],
            'l3stores': [self.getStatsGetter('L3', core, 'stores') for core in range(sim.config.ncores)],
            'uopbr': [self.getStatsGetter('interval_timer', core, 'uop_branch') for core in range(sim.config.ncores)],
            'uopfpaddsub': [self.getStatsGetter('interval_timer', core, 'uop_fp_addsub') for core in
                            range(sim.config.ncores)],
            'uopfpmuldiv': [self.getStatsGetter('interval_timer', core, 'uop_fp_muldiv') for core in
                            range(sim.config.ncores)],
            'uopgeneric': [self.getStatsGetter('interval_timer', core, 'uop_generic') for core in
                           range(sim.config.ncores)],
            'uopld': [self.getStatsGetter('interval_timer', core, 'uop_load') for core in range(sim.config.ncores)],
            'uopst': [self.getStatsGetter('interval_timer', core, 'uop_store') for core in range(sim.config.ncores)],
            'uoptotal': [self.getStatsGetter('interval_timer', core, 'uops_total') for core in
                         range(sim.config.ncores)],

        }

        args = dict(enumerate((args or '').split(':')))
        interval_ns = long(args.get(0, None) or 10000000)
        # scheduler_type = args.get(1, 'equal_time')
        # core_mask = args.get(2, '')
        # if scheduler_type == 'equal_time':
        #     self.getScoreMetric = getScoreMetricTime
        # elif scheduler_type == 'equal_instructions':
        #     self.getScoreMetric = getScoreMetricInstructions
        # else:
        #     raise ValueError('Invalid scheduler type %s' % scheduler_type)
        # if core_mask:
        #     core_mask = map(int, core_mask.split(',')) + [0]*sim.config.ncores
        #     self.cores = [ core for core in range(sim.config.ncores) if core_mask[core] ]
        # else:
        self.cores = range(sim.config.ncores)
        sim.util.Every(1000000 * sim.util.Time.NS, self.periodic, statsdelta = self.sd, roi_only=True)
        self.threads = {}
        self.last_core = 0

    def hook_thread_start(self, thread_id, time):
        self.threads[thread_id] = Thread(thread_id)
        self.threads[thread_id].runnable = True
        # Initial assignment: one thread per core until cores are exhausted
        if self.last_core < len(self.cores):
            self.threads[thread_id].setCore(self.cores[self.last_core], sim.stats.time())
            self.last_core += 1
        else:
            self.threads[thread_id].setCore(None, sim.stats.time())

    def hook_thread_exit(self, thread_id, time):
        self.hook_thread_stall(thread_id, 'exit', time)

    def hook_thread_stall(self, thread_id, reason, time):
        if reason == 'unscheduled':
            # Ignore calls due to the thread being scheduled out
            self.threads[thread_id].unscheduled = True
        else:
            core = self.threads[thread_id].core
            self.threads[thread_id].setCore(None, time)
            self.threads[thread_id].runnable = False
            # Schedule a new thread (runnable, but not running) on this free core
            threads = [ thread for thread in self.threads.values() if thread.runnable and thread.core is None ]
            if threads:
                # Order by score
                threads.sort(key = lambda thread: thread.score)
                threads[0].setCore(core, time)

    def hook_thread_resume(self, thread_id, woken_by, time):
        if self.threads[thread_id].unscheduled:
            # Ignore calls due to the thread being scheduled back in
            self.threads[thread_id].unscheduled = False
        else:
            self.threads[thread_id].setScore(max([ thread.score for thread in self.threads.values() ]))
            self.threads[thread_id].runnable = True
            #If there is a free core, move us there now
            used_cores = set([ thread.core for thread in self.threads.values() if thread.core is not None ])
            free_cores = set(self.cores) - used_cores
            if len(free_cores):
                self.threads[thread_id].setCore(list(free_cores)[0], time)

    def periodic(self, time, time_delta):

        # Update thread scores
        [ thread.updateScore(self.stats) for thread in self.threads.values() if thread.core is not None ]
        self.printPredectedIPC()
        # Get a list of all runnable threads
        threads = [ thread for thread in self.threads.values() if thread.runnable ]
        # Order by score
        threads.sort(key = lambda thread: thread.score, reverse=True)

        ##Debug
        print "not sorted list"
        for thread in threads:
            print thread.thread_id

        # Select threads to run now, one per core
        threads = [threads[0]] + threads[-len(self.cores)-1:]


        threads = sorted(set(threads), key=lambda  thread:thread.score, reverse=True)
        #print ', '.join(map(repr, threads))

        ##Debug
        print "Sorted List"
        for thread in threads:
            print thread.thread_id

        # Filter out threads that are already running, and keep them on their current core
        # keep_threads = [ thread for index, thread in enumerate(threads) if thread.core is not None and ((index in SMALL and thread.core in SMALL) or (index in BIG and thread.core in BIG))]
        # used_cores = set([ thread.core for thread in keep_threads])

        # # Move new threads to free cores
        # free_cores = set(self.cores) - used_cores
        #
        # ##Debug
        # print "free cores"
        # for core in free_cores:
        #     print core
        #
        # ##Debug
        # print "Free threads"
        # for thread in keep_threads:
        #     print thread.thread_id

        free_cores = [0 ,1, 2, 3]


        # threads = [ thread for thread in threads if thread.core is None ]
        assert(len(free_cores) >= len(threads))

        for thread, core in zip(threads, sorted(free_cores)):
            current_thread = [ t for t in self.threads.values() if t.core == core ]
            if current_thread:
                current_thread[0].setCore(None)

            thread.setCore(core, time)
            assert thread.runnable
        self.printInfo()

    def getStatsGetter(self, component, core, metric):
        # Some components don't exist (i.e. DRAM reads on cores that don't have a DRAM controller),
        # return a special object that always returns 0 in these cases
        try:
            return self.sd.getter(component, core, metric)
            print ""
        except:

            class Zero():
                def __init__(self): self.delta = 0

                def update(self): pass

            return Zero()

    def printInfo(self):
        print '----------- Quantum ', int(sim.stats.time() / 1e12), '------------'
        for thread in self.threads.values():
            print thread
        print 'idle:',
        for core in range(sim.config.ncores):
            print '%2.0f%%' % (
                100 * sim.stats.get('performance_model', core, 'idle_elapsed_time') / float(sim.stats.time())),
            print '%7d' % sim.stats.get('performance_model', core, 'idle_elapsed_time'),
        print '\nthreads:',
        for thread in range(sim.thread.get_nthreads()):
            print '%7dkins' % (sim.stats.get('thread', thread, 'instruction_count'))
        print '-----------------------'

    def printPredectedIPC(self):
        print "-------------- IPC's -----------"
        for thread in self.threads.values():
            if thread.core in BIG:
                print "Big ", thread.ipc, " Small* ", thread.predicted_ipc
            elif thread.core in SMALL:
                print "Big* ", thread.predicted_ipc, " Small ", thread.ipc
            print "--------------------------------"

sim.util.register(SchedulerLocality())
