import sys
import numpy as np
import math

fname = sys.argv[1]
quantums = []

with open(fname) as f:
    content = f.readlines()
content = [x.strip() for x in content]

count = 0
is_quantum = False
quantum = []

big_core_predicted_error = []
big_core_next_quantum_error = []

small_core_predicted_error = []
small_core_next_quantum_error = []

system_error = []

for line in content:
    if line.startswith("-----------"):
        quantum.append(line)
        is_quantum = True
    elif line.startswith("thread id :"):
        quantum.append(line)
        quantums.append(quantum)
        quantum = []
        is_quantum = False
    elif is_quantum:
        quantum.append(line)

threads = []

for thread in quantums[0][4:7]:
    threads.append(thread.split()[1:3])

threads.append(quantums[0][4].split()[1:3])

quantums = quantums[1:]

big_core_errors = []
small_core_errors = []
system_error = []

system_ann_error = []
system_nqp_error = []

system_ipc = []
quantum_count = 1
s_ipc = 0

for quantum in quantums:
    temp = []
    for line in quantum:
        if line[0].isdigit():
            temp.append(line.split()[1:3])

    s_predicted = 0
    s_real = 0

    sys_ann_error = []
    sys_nqp_error = []

    for prev_t, t in zip(threads, temp):
        if not t[0].startswith("*") and not t[0].startswith("?"):
            s_predicted += float(prev_t[0][1:] if prev_t[0].startswith("*") or prev_t[0].startswith("?") else prev_t[0])
            s_real += float(t[0][1:] if t[0].startswith("*") or t[0].startswith("?") else t[0])

            if prev_t[0].startswith("*") and not prev_t[0].startswith("?"):
                if float(t[0]) > 0.2:
                    err = abs(float(prev_t[0][1:]) - float(t[0])) / float(t[0])
                    sys_ann_error.append(err)

            if not prev_t[0].startswith("*") and not prev_t[0].startswith("?"):
                if float(t[0]) > 0.2:
                    err = abs(float(prev_t[0]) - float(t[0])) / float(t[0])
                    sys_nqp_error.append(err)

        if not t[1].startswith("*") and not t[1].startswith("?"):
            s_predicted += float(prev_t[1][1:] if prev_t[1].startswith("*") or prev_t[1].startswith("?") else prev_t[1])
            s_real += float(t[1][1:] if t[1].startswith("*") or t[1].startswith("?") else t[1])

            if prev_t[1].startswith("*") and not prev_t[1].startswith("?"):
                if float(t[1]) > 0.2:
                    err = abs(float(prev_t[1][1:]) - float(t[1])) / float(t[1])
                    sys_ann_error.append(err)

            if not prev_t[1].startswith("*") and not prev_t[1].startswith("?"):
                if float(t[1]) > 0.2:
                    err = abs(float(prev_t[1]) - float(t[1])) / float(t[1])
                    sys_nqp_error.append(err)

    if len(sys_nqp_error) > 0:
        avg_nqp_err = sum(sys_nqp_error) / len(sys_nqp_error)
        system_nqp_error.append(avg_nqp_err)

    if len(sys_ann_error) > 0:
        avg_ann_err = sum(sys_ann_error) / len(sys_ann_error)
        system_ann_error.append(avg_ann_err)
    if s_real > 0:
        system_error.append(abs(s_predicted - s_real) / s_real)
    threads = temp

system_nqp_u_error = sum(system_nqp_error) / len(system_nqp_error)
system_ann_u_error = sum(system_ann_error) / len(system_ann_error)
system_u_error = sum(system_error) / len(system_error)

system_nqp_std = 0
system_ann_std = 0
system_std = 0

for err in system_nqp_error:
    system_nqp_std += pow((err - system_nqp_u_error), 2)
system_nqp_std = system_nqp_std / len(system_nqp_error)
system_nqp_std = math.sqrt(system_nqp_std)


for err in system_ann_error:
    system_ann_std += pow((err - system_ann_u_error), 2)
system_ann_std = system_ann_std / len(system_nqp_error)
system_ann_std = math.sqrt(system_ann_std)

for err in system_error:
    system_std += pow((err - system_u_error), 2)
system_std = system_std / len(system_error)
system_std = math.sqrt(system_std)




with open("IpcError.txt", "a") as myfile:
    myfile.write(fname + "\nsystem mean : " + str(system_u_error) + "\nsystem std : " + str(system_std) + "\nsystem ann mean : " + str(system_ann_u_error) + "\nsystem ann std : " + str(system_ann_std) + "\nsystem nqp mean : " + str(system_nqp_u_error) + "\nsystem nqp std : " + str(system_nqp_std) + "\n\n")
