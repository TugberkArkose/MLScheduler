import sim
import os
import json
import itertools

#get number of threads set their ipc to something high in order to give them a chance to run then collect the real stats

class Scheduler:

    stats = {}
    path = "python /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/myNumpy0401.py "
    statsOrder = ['brhits', 'brmisses', 'dramreqs', 'dramreads', 'dramwrites', 'dtlbaccess', 'dtlbmisses', 'itlbaccess', 'itlbmisses', 'stlbaccess',
    'stlbmisses', 'dl1loads', 'dl1misses', 'dl1stores', 'il1loads', 'il1misses', 'l2loads', 'l2misses', 'l2stores',
    'l3loads', 'l3misses', 'l3stores', 'uopbr', 'uopfpaddsub', 'uopfpmuldiv', 'uopgeneric', 'uopld', 'uopst', 'uoptotal']
    num_threads = 0
    thread_ipc = []
    swapTimes = 0
    prev_bestcombination = ()
    finished_threads = []
    #const
    max_ipc = 120

    def setup(self, args):
        self.core_mapping = dict((core, '-') for core in range(sim.config.ncores))
        print sim.config.ncores
        self.icount_last = [0 for core in range(sim.config.ncores)]
        self.ipc = [0 for core in range(sim.config.ncores)]
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

        sim.util.Every(1000000 * sim.util.Time.NS, self.periodic, statsdelta = self.sd, roi_only=True)

    def hook_thread_migrate(self, threadid, coreid, time):
        self.core_mapping[coreid] = threadid
        self.swapTimes += 1

    def hook_thread_exit(self, thread_id, time):
        self.finished_threads.append(thread_id)

    def periodic(self, time, time_delta):

        if time_delta:
            for core in range(sim.config.ncores):
                # include fast-forward IPCs
                cycles = self.stats['time'][core].delta * sim.dvfs.get_frequency(core) / 1e9  # convert fs to cycles
                instrs = self.stats['coreinstrs'][core].delta
                self.ipc[core] = instrs / (cycles or 1)
            self.print_info()

        if time - self.last_reschedule >= 1000000:

            # change this to false to try pinned based scheduler
            if True:
                self.predict()
                self.last_reschedule = time

    def swapThreads(self, combination):

        if combination[0] not in self.finished_threads:
            sim.thread.set_thread_affinity(combination[0], ([1,0,0,0]))
        else:
            sim.thread.set_thread_affinity(combination[0], ([0, 0, 0, 0]))

        for t in range(1, 4):
            if combination[t] not in self.finished_threads:
                sim.thread.set_thread_affinity(combination[t], ([0,1,1,1]))
            else:
                sim.thread.set_thread_affinity(combination[t], ([0,0,0,0]))

        for i in range(0, self.num_threads):
            if i not in combination:
                sim.thread.set_thread_affinity(i, [0,0,0,0])

    def predict(self):
        best_combination = (-1, -1, -1, -1)
        best_ipc = 0

        thread_on_core0 = self.core_mapping[0]
        thread_on_core1 = self.core_mapping[1]
        thread_on_core2 = self.core_mapping[2]
        thread_on_core3 = self.core_mapping[3]

        print thread_on_core0, thread_on_core1, thread_on_core2, thread_on_core3

        self.core1_predicted = self.send_stats(0)
        self.core0_predicted_core1 = self.send_stats(1)
        self.core0_predicted_core2 = self.send_stats(2)
        self.core0_predicted_core3 = self.send_stats(3)

        self.thread_ipc[thread_on_core0] = [self.ipc[0], self.core1_predicted, self.core1_predicted, self.core1_predicted]
        self.thread_ipc[thread_on_core1] = [self.core0_predicted_core1, self.ipc[1], self.ipc[1], self.ipc[1]]
        self.thread_ipc[thread_on_core2] = [self.core0_predicted_core2, self.ipc[2], self.ipc[2], self.ipc[2]]
        self.thread_ipc[thread_on_core3] = [self.core0_predicted_core3, self.ipc[3], self.ipc[3], self.ipc[3]]

        for thread in self.finished_threads:
            self.thread_ipc[thread] = [0, 0, 0, 0]

        best_combination = list(best_combination)

        for thread in self.thread_ipc:
            print thread[0], thread[1], thread[2], thread[3]

        best0 = -1
        best1 = -1
        best2 = -1
        best3 = -1

        count = 0
        while -1 in best_combination:
            count += 1
            for idx, value in enumerate(self.thread_ipc):
                if value[0] >= best0 and idx not in best_combination:
                    best_combination[0] = idx
                    best0 = value[0]
                if value[1] > best1 and idx not in best_combination:
                    best_combination[1] = idx
                    best1 = value[1]
                if value[2] > best2 and idx not in best_combination:
                    best_combination[2] = idx
                    best2 = value[2]
                if value[3] > best3 and idx not in best_combination:
                    best_combination[3] = idx
                    best3 = value[3]
            if count > 9:
                best_combination = self.prev_bestcombination
                print "Stuck"
                break

        self.prev_bestcombination = best_combination

        # for i in range(len(self.thread_ipc)):
        #     for j in range(i+1, len(self.thread_ipc)):
        #         for o in range(j+1, len(self.thread_ipc)):
        #             for p in range(o+1, len(self.thread_ipc)):
        #                 for k, t, z, y in itertools.combinations([0,1,2,3], 4):
        #                     ipc = self.thread_ipc[i][k] + self.thread_ipc[j][t] + self.thread_ipc[o][z] + self.thread_ipc[p][y]
        #                     print ipc
        #                     if ipc >= best_ipc:
        #                         print i,k,j,t,o,z,p,y
        #                         best_ipc = ipc
        #
        #                         best_combination = list(best_combination)
        #                         best_combination.insert(k, i)
        #                         best_combination.insert(t, j)
        #                         best_combination.insert(z, o)
        #                         best_combination.insert(y, p)

        best_combination = tuple(best_combination)
        print best_combination
        self.swapThreads(best_combination)

    def send_stats(self, core):

        statlist = []

        if core == 0:
            statlist.append(self.ipc[core])
            for key in self.statsOrder:
                statlist.append((self.stats[key])[core].delta)
            jlist = json.dumps(statlist, separators=(',', ':'))
            proc = os.popen( self.path +str(core) + " " + jlist).read()
            #result = json.loads(proc)
            #code above does not work check why
            result = proc
            fresult = float(result)
            return fresult

        if core == 1:
            statlist.append(self.ipc[core])
            for key in self.statsOrder:
                statlist.append((self.stats[key])[core].delta)
            jlist = json.dumps(statlist, separators=(',', ':'))
            proc = os.popen(self.path +str(core)+ " " + jlist).read()
            #result = json.loads(proc)
            #code above does not work check why
            result = proc
            fresult = float(result)
            return fresult

        if core == 2:
            statlist.append(self.ipc[core])
            for key in self.statsOrder:
                statlist.append((self.stats[key])[core].delta)
            jlist = json.dumps(statlist, separators=(',', ':'))
            proc = os.popen(self.path +str(1)+ " " + jlist).read()
            #result = json.loads(proc)
            #code above does not work check why
            result = proc
            fresult = float(result)
            return fresult

        if core == 3:
            statlist.append(self.ipc[core])
            for key in self.statsOrder:
                statlist.append((self.stats[key])[core].delta)
            jlist = json.dumps(statlist, separators=(',', ':'))
            proc = os.popen(self.path +str(1)+ " " + jlist).read()
            #result = json.loads(proc)
            #code above does not work check why
            result = proc
            fresult = float(result)
            return fresult


    def print_info(self):
        print '----------- Quantum ', int(sim.stats.time() / 1e12), '------------'
        print 'mapping:', ' '.join(str(self.core_mapping[core]) for core in range(sim.config.ncores))
        print 'ipc:', ' '.join('%3.1f' % self.ipc[core] for core in range(sim.config.ncores))
        print 'idle:',
        for core in range(sim.config.ncores):
            print '%2.0f%%' % (
                100 * sim.stats.get('performance_model', core, 'idle_elapsed_time') / float(sim.stats.time())),
            print '%7d' % sim.stats.get('performance_model', core, 'idle_elapsed_time'),
        print '\nthreads:',
        for thread in range(sim.thread.get_nthreads()):
            print '%7dkins' % (sim.stats.get('thread', thread, 'instruction_count')),
        print '\nNumber of Swaps: ', self.swapTimes
        print 'Total ipc: ', (self.ipc[0] + self.ipc[1])
        # print 'Thread 0 ', self.thread_ipc[0]
        # print 'Thread 1', self.thread_ipc[1]
        # print 'Thread 2', self.thread_ipc[2]
        # print 'Thread 3', self.thread_ipc[3]
        print '-----------------------'

    def hook_roi_end(self):
        print
        print 'Total runtime = %d us' % (sim.stats.time() / 1e9)
        print

    def hook_thread_start(self, threadid, creator):
        self.num_threads = sim.thread.get_nthreads()
        self.thread_ipc.append((self.max_ipc, self.max_ipc))


    def getStatsGetter(self, component, core, metric):
        # Some components don't exist (i.e. DRAM reads on cores that don't have a DRAM controller),
        # return a special object that always returns 0 in these cases
        try:
            return self.sd.getter(component, core, metric)
        except:
            print "Get Stats Getter"
            class Zero():
                def __init__(self): self.delta = 0

                def update(self): pass

            return Zero()


sim.util.register(Scheduler())
