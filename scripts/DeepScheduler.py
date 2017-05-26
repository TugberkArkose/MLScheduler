import os
import json
import itertools
import sim
import operator
from collections import defaultdict

BIG = [0]
SMALL = [1,2,3]
PATH = "python /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/deepnet.py "
#PATH = "python /home/tugberk/Bsc/DaniThesis/myNumpy0102.py "
STATSORDER = ['brhits', 'brmisses', 'dramreqs', 'dramreads', 'dramwrites', 'dtlbaccess', 'dtlbmisses', 'itlbaccess', 'itlbmisses', 'stlbaccess',
    'stlbmisses', 'dl1loads', 'dl1misses', 'dl1stores', 'il1loads', 'il1misses', 'il1stores','l2loads', 'l2misses', 'l2stores',
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
        self.BigIpc = 0.1
        self.SmallIpc = 0.1
        self.score = 0       # Accumulated score
        self.prevIPC = 0.1
        self.prevCore = None
        sim.thread.set_thread_affinity(self.thread_id, ())


    def updateScore(self, stats):
        cycles = stats['time'][self.core].delta * sim.dvfs.get_frequency(self.core) / 1e9  # convert fs to cycles
        instrs = stats['coreinstrs'][self.core].delta

        if self.core in BIG:
            self.prevIPC = self.BigIpc
            self.BigIpc = instrs / (cycles or 1)
            self.SmallIpc = self.send_stats(stats)
        elif self.core in SMALL:
            self.prevIPC = self.SmallIpc
            self.SmallIpc = instrs / (cycles or 1)
            self.BigIpc = self.send_stats(stats)

        if self.SmallIpc == 0:
            self.SmallIpc = 0.1

        self.score = self.BigIpc / self.SmallIpc


    def setScore(self, score):
        self.score = score

    def setCore(self, core_id, time = -1):
        self.prevCore = self.core
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
            statlist.append(self.BigIpc)

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
            statlist.append(self.SmallIpc)

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
        r = str(self.thread_id) + " "
        if self.core in BIG:
            r += "   " + "{:.4f}".format(self.BigIpc) + "  "
            r += "  *" + "{:.4f}".format(self.SmallIpc) + "  "
        elif self.core in SMALL:
            r += "  *" + "{:.4f}".format(self.BigIpc) + "  "
            r += "   " + "{:.4f}".format(self.SmallIpc) + "  "
        else:
            r += "  ?" + "{:.4f}".format(self.BigIpc) + "  "
            r += "  ?" + "{:.4f}".format(self.SmallIpc) + "  "
        r += "{:.4f}".format(self.score) + " "
        r += "R       " if self.runnable else "W       "
        if self.core is not None:
            r += str(self.core)
        else:
            r += "N"
        return r


class SchedulerLocality:
    predicted_ipc = 0
    predicted_mapping = []
    prev_predicted_ipc = 0
    prediction_gap = []

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
            'il1stores': [self.getStatsGetter('L1-I', core, 'stores') for core in range(sim.config.ncores)],
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

        # Get a list of all runnable threads
        threads = [ thread for thread in self.threads.values() if thread.runnable ]
        # Order by score
        threads.sort(key = lambda thread: thread.score, reverse=True)

        combination_size = len(BIG) + len(SMALL)

        combination_big = (sorted(threads, key= lambda thread: thread.BigIpc, reverse=True)[:combination_size])
        combination_small = (sorted(threads, key = lambda thread: thread.SmallIpc, reverse=True))[:combination_size]


        highest_ipc = 0
        best_combination = []

        for big_thread in combination_big:
            current_ipc = big_thread.BigIpc
            current_combination = [big_thread]
            for small_thread in combination_small:
                if big_thread.thread_id != small_thread.thread_id:
                    current_ipc += small_thread.SmallIpc
                    current_combination.append(small_thread)
            if current_ipc > highest_ipc:
                highest_ipc = current_ipc
                best_combination = current_combination

        self.prev_predicted_ipc = self.predicted_ipc
        self.predicted_ipc = highest_ipc
        self.predicted_mapping = best_combination
        self.printInfo()
        threads = best_combination

        free_cores = [0, 1, 2, 3]
        # threads = [ thread for thread in threads if thread.core is None ]
        assert(len(free_cores) >= len(threads))
        for thread, core in zip(threads, sorted(free_cores)):
            current_thread = [ t for t in self.threads.values() if t.core == core ]
            if current_thread:
                if current_thread[0].thread_id == thread.thread_id:
                    continue
                current_thread[0].setCore(None)

            thread.setCore(core, time)
            assert thread.runnable


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

    def testPrint(self):
        print '----------- Quantum ', int(sim.stats.time() / 1e12), '------------'
        total_ipc = 0
        for thread in self.threads.values():
            if thread.core in BIG:
                total_ipc += thread.BigIpc
            elif thread.core in SMALL:
                total_ipc += thread.SmallIpc
            print thread
        # print 'idle:',
        # for core in range(sim.config.ncores):
        #     print '%2.0f%%' % (
        #         100 * sim.stats.get('performance_model', core, 'idle_elapsed_time') / float(sim.stats.time())),
        #     print '%7d' % sim.stats.get('performance_model', core, 'idle_elapsed_time'),
        # print '\nthreads:',
        # for thread in range(sim.thread.get_nthreads()):
        #     print '%7dkins' % (sim.stats.get('thread', thread, 'instruction_count'))
        print '-----------------------'

    def printInfo(self):
        print '----------- Quantum ', int(sim.stats.time() / 1e12), '------------'
        total_ipc = 0
        for thread in self.threads.values():
            if thread.core in BIG:
                total_ipc += thread.BigIpc
            elif thread.core in SMALL:
                total_ipc += thread.SmallIpc
        print "System IPC : " + str(total_ipc)

        mapping = "[ "
        core_mapping = defaultdict(list)
        for thread in self.threads.values():
            core_mapping[thread.core] = thread.thread_id
        for i in range(0, (len(BIG) + len(SMALL))):
            if core_mapping[i] or core_mapping[i] == 0:
                mapping += str(core_mapping[i]) +" "
            else:
                mapping += "- "
        mapping +="]"

        if(int(sim.stats.time() / 1e12) > 1):
            print "Misprediction : " + str(total_ipc - self.prev_predicted_ipc)
            self.prediction_gap.append(total_ipc - self.predicted_ipc)

        print "System Map " + mapping

        print "TId  " + "B          " + "S       " + "Sc     " + "Status  " + "Core"
        for thread in self.threads.values():
            print thread
        print "*System IPC : " + str(self.predicted_ipc)

        mapping = "[ "
        core_mapping_predicted = defaultdict(list)
        for idx, thread in enumerate(self.predicted_mapping):
            core_mapping_predicted[idx] = thread.thread_id
        for i in range(0, (len(BIG) + len(SMALL))):
            if core_mapping_predicted[i] or core_mapping_predicted[i] == 0:
                mapping += str(core_mapping_predicted[i]) +" "
            else:
                mapping += "- "
        mapping +="]"
        print "*System Map " + mapping

        if(int(sim.stats.time() / 1e12) > 1):
            print "Avarage system misprediction : " + str(sum(self.prediction_gap) / len(self.prediction_gap))

        for thread in self.threads.values():
            if (thread.core in BIG and thread.prevCore in SMALL):
                print "thread id : ", str(thread.thread_id), " misprediction s2b : ", str(thread.BigIpc - thread.prevIPC)
            elif (thread.core in SMALL and thread.prevCore in BIG):
                print "thread id : ", str(thread.thread_id), " misprediction b2s : ", str(thread.SmallIpc - thread.prevIPC)


sim.util.register(SchedulerLocality())
