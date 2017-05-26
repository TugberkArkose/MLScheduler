import sys
import os
import json
import itertools
import sim
import operator
from collections import defaultdict

BIG = [0]
SMALL = [1,2,3]
#PATH = "python /scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/myNumpy0102.py "
PATH = "python /scratch/nas/1/dn/sniper-6.0/scripts/predictor_blackbox.py "
MODELNAME = "/scratch/nas/1/dn/sniper-6.0/scripts/MICRO_sys_predictor_full_trained.p"

accumulated_stats = []

#STATSORDER = ['brhits', 'brmisses', 'dramreqs', 'dramreads', 'dramwrites', 'dtlbaccess', 'dtlbmisses', 'itlbaccess', 'itlbmisses', 'stlbaccess',
#    'stlbmisses', 'dl1loads', 'dl1misses', 'dl1stores', 'il1loads', 'il1misses', 'il1stores','l2loads', 'l2misses', 'l2stores',
#    'l3loads', 'l3misses', 'l3stores', 'uopbr', 'uopfpaddsub', 'uopfpmuldiv', 'uopgeneric', 'uopld', 'uopst', 'uoptotal']

params_to_use_per_thread = ['uopBR_Norm', 'uopFPtotal_Norm', 'uopGeneric_Norm', 'uopLD_Norm', 'DL1miss_Norm', 'L2miss_Norm','L3miss_Norm',
      'IL1ld_div_DL1ld_Norm', 'L2miss_div_DL1miss_Norm','L3miss_div_L2miss_Norm', 'L3miss_div_DL1miss_Norm'] # 11 in total

STATSORDER = [['/', 'uopbr', 'uoptotal'], ['/', ['+', 'uopfpaddsub', 'uopfpmuldiv'], 'uoptotal'], ['/', 'uopgeneric', 'uoptotal'],
    ['/', 'uopld', 'uoptotal'], ['/', 'uopst', 'uoptotal'], ['/','dl1misses', ['+', 'dl1loads', 'dl1stores']], ['/','l2misses', ['+','l2loads', 'l2stores']],['/', 'l3misses', ['+', 'l3loads', 'l3stores']],
    ['/', 'il1loads', 'dl1loads'], ['/', 'l2misses', 'dl1misses'], ['/', 'l3misses', 'l2misses'], ['/', 'l3misses', 'dl1misses']]

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
        self.getScoreMetric = lambda: getScoreMetricInstructions(thread_id)
        self.score = 0       # Accumulated score
        self.prevIPC = 0.1
        self.prevCore = None
        self.train_cycle = 1
        self.ipc = 0
        self.cycles = 0
        self.mapping = []

        self.thread_stats = []

        self.hetero_score = 0       # Accumulated fairness score
        self.metric_last = 0        # State at start of last interval

        sim.thread.set_thread_affinity(self.thread_id, ())


    def updateScore(self, stats):
        self.cycles = stats['time'][self.core].delta * sim.dvfs.get_frequency(self.core) / 1e9  # convert fs to cycles
        instrs = stats['coreinstrs'][self.core].delta
        self.ipc = instrs / (self.cycles or 1)

        metric_now = self.getScoreMetric()
        self.hetero_score += metric_now - self.metric_last
        self.metric_last = metric_now

        self.thread_stats = self.getStats(stats)

    def getStats(self, stats):
        result = []
        value1 = 0
        value2 = 0
        for key in STATSORDER:
            if type(key) == list:
                if type(key[1]) == list:
                    k_value1 = (stats[key[1][1]])[self.core].delta
                    k_value2 = (stats[key[1][2]])[self.core].delta
                    if key[1][0] == '/':
                        if k_value2 != 0:
                            value1 = (k_value1 / k_value2)
                        else:
                            value1 = 0
                    elif key[1][0] == '+':
                        value1 = (k_value1 + k_value2)
                else:
                    value1 = (stats[key[1]])[self.core].delta
                if type(key[2]) == list:
                    k_value1 = (stats[key[2][1]])[self.core].delta
                    k_value2 = (stats[key[2][2]])[self.core].delta
                    if key[2][0] == '/':
                        if k_value2 != 0:
                            value2 = (k_value1 / k_value2)
                        else:
                            value1 = 0
                    elif key[2][0] == '+':
                        value2 = (k_value1 + k_value2)
                else:
                    value2 = (stats[key[2]])[self.core].delta
                if key[0] == '/':
                    if value2 != 0:
                        result.append(value1 / value2)
                    else:
                        result.append(0)
                elif key[0] == '+':
                    result.append(value1 + value2)
            else:
                result.append((stats[key])[self.core].delta)
        return result

    def normalizeStats(self, stats):
        normalized_stats = []
        for index, value in enumerate(stats):
            min_value = self.getMin(self.accumulated_non_normalized_stats, index)
            max_value = self.getMax(self.accumulated_non_normalized_stats, index)
            normalized_stats.append((value - min_value) / (max_value - min_value))
        return normalized_stats

    def getMax(self, accumulated_non_normalized_stats, index):
        max_value = -5000
        for stat_list in accumulated_non_normalized_stats:
            if stat_list[index] > max_value:
                max_value = stat_list[index]
        return max_value

    def getMin(self, accumulated_non_normalized_stats, index):
        min_value = 5000
        for stat_list in accumulated_non_normalized_stats:
            if stat_list[index] < min_value:
                min_value = stat_list[index]
        return min_value


    def updateHeteroScore(self):
        metric_now = self.getScoreMetric()
        self.hetero_score += metric_now - self.metric_last
        self.metric_last = metric_now

    def setScore(self, score):
        self.score = score

    def setHeteroScore(self, hetero_score):
        self.hetero_score = hetero_score
        self.metric_last = self.getScoreMetric()

    def setCore(self, core_id, time = -1):
        self.prevCore = self.core
        self.core = core_id
        if core_id is None:
            self.updateHeteroScore()
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
            r += "   " + "{:.4f}".format(self.ipc) + "  "
            r += "  *" + "{:.4f}".format(self.ipc) + "  "
        elif self.core in SMALL:
            r += "  *" + "{:.4f}".format(self.ipc) + "  "
            r += "   " + "{:.4f}".format(self.ipc) + "  "
        else:
            r += "  ?" + "{:.4f}".format(self.ipc) + "  "
            r += "  ?" + "{:.4f}".format(self.ipc) + "  "
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
    train_cycle = 0
    train_data = []
    sum_ipc = 0
    system_ipcs = []
    hetero_timer = 0
    sum_square = 0
    sum_perct = 0
    sum_err = 0

    def setup(self, args):
        print "setup"
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
        scheduler_type = args.get(1, 'equal_instructions')
        core_mask = args.get(2, '')
        if scheduler_type == 'equal_time':
            self.getScoreMetric = getScoreMetricTime
        elif scheduler_type == 'equal_instructions':
            self.getScoreMetric = getScoreMetricInstructions
        else:
            raise ValueError('Invalid scheduler type %s' % scheduler_type)
        if core_mask:
            core_mask = map(int, core_mask.split(',')) + [0]*sim.config.ncores
            self.cores = [ core for core in range(sim.config.ncores) if core_mask[core] ]
        else:
            self.cores = range(sim.config.ncores)
        sim.util.Every(1000000 * sim.util.Time.NS, self.periodic, statsdelta = self.sd, roi_only=True)
        self.threads = {}
        self.last_core = 0

    # def hook_thread_start(self, thread_id, time):
    #     self.threads[thread_id] = Thread(thread_id)
    #     self.threads[thread_id].runnable = True
    #     # Initial assignment: one thread per core until cores are exhausted
    #     if self.last_core < len(self.cores):
    #         self.threads[thread_id].setCore(self.cores[self.last_core], sim.stats.time())
    #         self.last_core += 1
    #     else:
    #         self.threads[thread_id].setCore(None, sim.stats.time())
    #
    # def hook_thread_exit(self, thread_id, time):
    #     self.hook_thread_stall(thread_id, 'exit', time)
    #
    # def hook_thread_stall(self, thread_id, reason, time):
    #     if reason == 'unscheduled':
    #         # Ignore calls due to the thread being scheduled out
    #         self.threads[thread_id].unscheduled = True
    #     else:
    #         core = self.threads[thread_id].core
    #         self.threads[thread_id].setCore(None, time)
    #         self.threads[thread_id].runnable = False
    #         # Schedule a new thread (runnable, but not running) on this free core
    #         threads = [ thread for thread in self.threads.values() if thread.runnable and thread.core is None ]
    #         if threads:
    #             # Order by score
    #             threads.sort(key = lambda thread: thread.score)
    #             threads[0].setCore(core, time)
    #
    # def hook_thread_resume(self, thread_id, woken_by, time):
    #     if self.threads[thread_id].unscheduled:
    #         # Ignore calls due to the thread being scheduled back in
    #         self.threads[thread_id].unscheduled = False
    #     else:
    #         self.threads[thread_id].setHeteroScore(max([ thread.hetero_score for thread in self.threads.values() ]))
    #         self.threads[thread_id].runnable = True
    #         #If there is a free core, move us there now
    #         used_cores = set([ thread.core for thread in self.threads.values() if thread.core is not None ])
    #         free_cores = set(self.cores) - used_cores
    #         if len(free_cores):
    #             self.threads[thread_id].setCore(list(free_cores)[0], time)

    def getSystemIPCForPreviousQuantum(self, threads):
        system_ipc = 0
        for thread in threads:
            system_ipc += thread.ipc
        return system_ipc

    def updateTrainData(self, threads_to_train):
        temp = []

        for thread in threads_to_train:
            if thread.thread_stats:
                temp.extend(thread.thread_stats)
            else:
                temp.extend([0]*len(STATSORDER))

        ipc = self.getSystemIPCForPreviousQuantum(threads_to_train)
        self.system_ipcs.append(ipc)
        self.train_data.append(temp)

    def predict(self, a, b, c, d):
        a = json.dumps(a, separators=(',', ':'))
        b = json.dumps(b, separators=(',', ':'))
        c = json.dumps(c, separators=(',', ':'))
        d = json.dumps(d, separators=(',', ':'))

        proc = os.popen(PATH + str(1) + " " + MODELNAME + " " + a + " " + b + " " + c + " " + d).read()
        #result = json.loads(proc)
        #code above does not work check why
        result = proc
        #print(result)
        #do sys call
        #syscall(train_data)
        return result

    def findThread(self, threads, thread_id):
        for thread in threads:
            if thread.thread_id == thread_id:
                return thread


    def periodic(self, time, time_delta):
        # order = ""
        # # Update mapper thread scores
        # [ thread.updateScore(self.stats) for thread in self.threads.values() if thread.core is not None ]
        #
        # # threads_to_train = [ thread for thread in self.threads.values() if thread.core is not None ]
        # # threads_to_train.sort(key = lambda thread: thread.core)
        #
        # #self.updateTrainData(threads_to_train)
        # #train
        # #self.train(self.train_data)
        #
        # # Get a list of all runnable threads
        # threads = [ thread for thread in self.threads.values() if thread.runnable ]
        #
        # # Order by score
        # threads.sort(key = lambda thread: thread.thread_id, reverse=True)
        #
        # combination_size = len(BIG) + len(SMALL)
        #
        # threads = threads[:combination_size]
        # # if len(threads) >= combination_size:
        # #     if int(sim.stats.time() / 1e12) > 2:
        # #         a = threads[0].thread_stats
        # #         b = threads[1].thread_stats
        # #         c = threads[2].thread_stats
        # #         d = threads[3].thread_stats
        # #         if a and b and c and d:
        # #             self.predicted_mapping = self.predict(a, b, c, d)
        # #             if len(self.predicted_mapping) > 5:
        # #                 order = self.predicted_mapping[:4]
        # #                 self.prev_predicted_ipc = self.predicted_ipc
        # #                 self.predicted_ipc = self.predicted_mapping[4:]
        # #                 self.predicted_ipc = float(''.join(self.predicted_ipc))
        # #                 #print self.predicted_ipc
        # #                 #print order
        # #                 temp = []
        # #                 temp.append(self.findThread(threads, int(order[0])))
        # #                 temp.append(self.findThread(threads, int(order[1])))
        # #                 temp.append(self.findThread(threads, int(order[2])))
        # #                 temp.append(self.findThread(threads, int(order[3])))
        # #                 threads = temp
        #
        # free_cores = [0, 1, 2, 3]
        # # threads = [ thread for thread in threads if thread.core is None ]
        # assert(len(free_cores) >= len(threads))
        # for thread, core in zip(threads, sorted(free_cores)):
        #     current_thread = [ t for t in self.threads.values() if t.core == core ]
        #     if current_thread:
        #         if current_thread[0].thread_id == thread.thread_id:
        #             continue
        #         current_thread[0].setCore(None)
        #
        #     thread.setCore(core, time)
        #     assert thread.runnable

        # combination_big = (sorted(threads, key= lambda thread: thread.BigIpc, reverse=True)[:combination_size])
        # combination_small = (sorted(threads, key = lambda thread: thread.SmallIpc, reverse=True))[:combination_size]
        #
        # highest_ipc = 0
        # best_combination = []
        #
        # for big_thread in combination_big:
        #     current_ipc = big_thread.BigIpc
        #     current_combination = [big_thread]
        #     for small_thread in combination_small:
        #         if big_thread.thread_id != small_thread.thread_id:
        #             current_ipc += small_thread.SmallIpc
        #             current_combination.append(small_thread)
        #     if current_ipc > highest_ipc:
        #         highest_ipc = current_ipc
        #         best_combination = current_combination
        #
        # self.prev_predicted_ipc = self.predicted_ipc
        # self.predicted_ipc = highest_ipc
        # self.predicted_mapping = best_combination
        self.printInfo()
        # threads = best_combination
        #
        # free_cores = [0, 1, 2, 3]
        # # threads = [ thread for thread in threads if thread.core is None ]
        # assert(len(free_cores) >= len(threads))
        # for thread, core in zip(threads, sorted(free_cores)):
        #     current_thread = [ t for t in self.threads.values() if t.core == core ]
        #     if current_thread:
        #         if current_thread[0].thread_id == thread.thread_id:
        #             continue
        #         current_thread[0].setCore(None)
        #
        #     thread.setCore(core, time)
        #     assert thread.runnable


    def train(self, train_data):
        if self.train_cycle == 20:
            jlist = json.dumps(train_data, separators=(',', ':'))
            statList = json.dumps(self.system_ipcs, separators=(',', ':'))
            proc = os.popen(PATH + str(0) + " " + MODELNAME + " " + jlist + " " + statList + " ").read()
            #result = json.loads(proc)
            #code above does not work check why
            result = proc
            #do sys call
            #syscall(train_data)
            self.train_cycle = 0
            self.train_data = []
            self.system_ipcs = []
        self.train_cycle += 1

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

    def get_quantum_squareError(self,pred,y):
        #pred is the predicted system IPC value and y is the observed IPC value after quantum
        e = (pred-y)**2
        return e

    def get_quantum_percentError(self,pred,y):
        #pred is the predicted system IPC value and y is the observed IPC value after quantum
        e = abs(pred-y)/y
        return e

    def printInfo(self):
        print '----------- Quantum ', int(sim.stats.time() / 1e12), '------------'
        total_ipc = 0
        for thread in self.threads.values():
                total_ipc += thread.ipc
        print "System IPC : " + str(total_ipc)

        self.sum_ipc += total_ipc
        print "Avg Ipc : " + str(self.sum_ipc / int(sim.stats.time() / 1e12))

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

        # if(int(sim.stats.time() / 1e12) > 1):
        #     print "Misprediction : " + str(total_ipc - self.prev_predicted_ipc)
        #     self.sum_err += total_ipc - self.prev_predicted_ipc
        #     print "Avg Mispredicrion : " + str(self.sum_err / int(sim.stats.time() / 1e12))
        # print "Predicted Ipc : " + str(self.predicted_ipc)
        print "System Map " + mapping
        # self.sum_square += self.get_quantum_squareError(self.prev_predicted_ipc, total_ipc)
        # self.sum_perct += self.get_quantum_percentError(self.prev_predicted_ipc, total_ipc)
        # print "Quantum Square Error : " + str(self.get_quantum_squareError(self.prev_predicted_ipc, total_ipc))
        # print "Avarage qse : " + str(self.sum_square / int(sim.stats.time() / 1e12))
        # print "Avarage perct error : " + str(self.sum_perct / int(sim.stats.time() / 1e12))
        # print "Quantum Percent Error : " + str(self.get_quantum_percentError(self.prev_predicted_ipc, total_ipc))
        print "TId  " + "B          " + "S       " + "Sc     " + "Status  " + "Core"
        for thread in self.threads.values():
            print thread
        # print "*System IPC : " + str(self.predicted_ipc)
        #
        # mapping = "[ "
        # core_mapping_predicted = defaultdict(list)
        # for idx, thread in enumerate(self.predicted_mapping):
        #     core_mapping_predicted[idx] = thread.thread_id
        # for i in range(0, (len(BIG) + len(SMALL))):
        #     if core_mapping_predicted[i] or core_mapping_predicted[i] == 0:
        #         mapping += str(core_mapping_predicted[i]) +" "
        #     else:
        #         mapping += "- "
        # mapping +="]"
        # print "*System Map " + mapping

        # if(int(sim.stats.time() / 1e12) > 1):
        #     print "Avarage system misprediction : " + str(sum(self.prediction_gap) / len(self.prediction_gap))

        # for thread in self.threads.values():
        #     if (thread.core in BIG and thread.prevCore in SMALL):
        #         print "thread id : ", str(thread.thread_id), " misprediction s2b : ", str(thread.BigIpc - thread.prevIPC)
        #     elif (thread.core in SMALL and thread.prevCore in BIG):
        #         print "thread id : ", str(thread.thread_id), " misprediction b2s : ", str(thread.SmallIpc - thread.prevIPC)



sim.util.register(SchedulerLocality())
