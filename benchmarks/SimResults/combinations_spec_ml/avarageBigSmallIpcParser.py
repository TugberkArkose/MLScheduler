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
big_core_predicted_error = []
big_core_next_quantum_error = []

small_core_errors = []
small_core_predicted_error = []
small_core_next_quantum_error = []

system_error = []
system_predicted_error = []
system_next_quantum_error = []

system_ipc = []
quantum_count = 1
s_ipc = 0

for quantum in quantums:
    temp = []
    for line in quantum:
        if line[0].isdigit():
            temp.append(line.split()[1:3])
    small_errors = []
    small_predicted_error = []
    small_next_quantum_error =[]
    s_predicted = 0
    s_real = 0
    s_ml_predicted = 0
    s_ml_predicted_real = 0
    s_next_quantum = 0
    s_next_quantum_real = 0

    for prev_t, t in zip(threads, temp):
        if not t[0].startswith("*") and not t[0].startswith("?"):
            big_core_errors.append([t[0], prev_t[0]])
            s_predicted += float(prev_t[0][1:] if prev_t[0].startswith("*") or prev_t[0].startswith("?") else prev_t[0])
            s_real += float(t[0][1:] if t[0].startswith("*") or t[0].startswith("?") else t[0])
            if prev_t[0].startswith("*") and not prev_t[0].startswith("?"):
                big_core_predicted_error.append([t[0], prev_t[0][1:]])
                s_ml_predicted += float(prev_t[0][1:])
                s_ml_predicted_real += float(t[0])
            if not prev_t[0].startswith("*") and not prev_t[0].startswith("?"):
                big_core_next_quantum_error.append([t[0], prev_t[0]])
                s_next_quantum += float(prev_t[0])
                s_next_quantum_real += float(t[0])
            s_ipc += s_real
        if not t[1].startswith("*") and not t[1].startswith("?"):
            small_errors.append([t[1], prev_t[1]])
            s_predicted += float(prev_t[1][1:] if prev_t[1].startswith("*") or prev_t[1].startswith("?") else prev_t[1])
            s_real += float(t[1][1:] if t[1].startswith("*") or t[1].startswith("?") else t[1])
            s_ipc += s_real
            if prev_t[1].startswith("*") and not prev_t[1].startswith("?"):
                small_predicted_error.append([t[1], prev_t[1][1:]])
                s_ml_predicted += float(prev_t[1][1:])
                s_ml_predicted_real += float(t[1])
            if not prev_t[1].startswith("*") and not prev_t[1].startswith("?"):
                small_next_quantum_error.append([t[1], prev_t[1]])
                s_next_quantum += float(prev_t[1])
                s_next_quantum_real += float(t[1])
    quantum_count += 1
    system_ipc.append([quantum_count, s_real])
    quantum_count += 1
    system_error.append([s_real, s_predicted])
    threads = temp
    small_core_errors.append(small_errors)
    small_core_predicted_error.append(small_predicted_error)
    small_core_next_quantum_error.append(small_next_quantum_error)
    system_predicted_error.append([s_ml_predicted_real, s_ml_predicted])
    system_next_quantum_error.append([s_next_quantum_real, s_next_quantum])

big_mean_square_error = 0
small_mean_square_error = 0

big_percentage_error = []
small_percentage_error = []

diff_small = []
diff_big = []

system_mean_square_error = 0
system_percentage_error = []
diff_system = []

system_predicted_mean_square_error = 0
system_next_quantum_mean_square_error = 0
small_core_predicted_mean_square_error = 0
small_core_next_quantum_mean_square_error = 0
big_core_predicted_mean_square_error = 0
big_core_next_quantum_mean_square_error = 0

big_err = []

for big_error in big_core_errors:
    if big_error[1].startswith("*") or big_error[1].startswith("?"):
        big_error[1] = big_error[1][1:]

    big_error = np.array(big_error)
    big_error = big_error.astype(np.float)

    if big_error[0] == 0:
        continue

    big_err.append(((abs(big_error[1] - big_error[0])) / big_error[0]))

    big_percentage_error.append((big_error[1] - big_error[0]) / big_error[0])
    diff_big.append(big_error[1] - big_error[0])

big_uerr = sum(big_err) / len(big_err)

big_std_err = 0

for err in big_err:
    big_std_err += pow((err - big_uerr), 2)
big_std_err = math.sqrt(big_std_err / len(big_err))


#=================

big_err_pred = []

for big_error in big_core_predicted_error:
    if big_error[1].startswith("*") or big_error[1].startswith("?"):
        big_error[1] = big_error[1][1:]

    big_error = np.array(big_error)
    big_error = big_error.astype(np.float)

    if big_error[0] == 0:
        continue

    big_err_pred.append(((abs(big_error[1] - big_error[0])) / big_error[0]))

big_uerr_pred = sum(big_err_pred) / len(big_err_pred)

big_core_predicted_mean_square_error = 0

for err in big_err_pred:
    big_core_predicted_mean_square_error += pow((err - big_uerr_pred), 2)
big_core_predicted_mean_square_error = math.sqrt(big_core_predicted_mean_square_error / len(big_err_pred))

#=================

#=================

big_err_next = []

for big_error in big_core_next_quantum_error:
    if big_error[1].startswith("*") or big_error[1].startswith("?"):
        big_error[1] = big_error[1][1:]

    big_error = np.array(big_error)
    big_error = big_error.astype(np.float)

    if big_error[0] == 0:
        continue

    big_err_next.append(((abs(big_error[1] - big_error[0])) / big_error[0]))

big_uerr_next = sum(big_err_next) / len(big_err_next)

big_core_next_quantum_mean_square_error = 0

for err in big_err_next:
    big_core_next_quantum_mean_square_error += pow((err - big_uerr_next), 2)
big_core_next_quantum_mean_square_error = math.sqrt(big_core_next_quantum_mean_square_error / len(big_err_next))

#=================

#=================

small_error_pred = []
for small_error_quantum in small_core_predicted_error:
    s_p = 0
    s_r = 0
    for small_error in small_error_quantum:
        if small_error[1].startswith("*") or small_error[1].startswith("?"):
            small_error[1] = small_error[1][1:]

        small_error = np.array(small_error)
        small_error = small_error.astype(np.float)

        if small_error[0] == 0:
            continue
        s_p += small_error[1]
        s_r += small_error[0]
    if len(small_error_quantum) == 0:
        continue
    s_p = s_p / len(small_error_quantum)
    s_r = s_r / len(small_error_quantum)
    small_error_pred.append(abs(s_p - s_r) / s_r)

small_uerror_pred = sum(small_error_pred) / len(small_error_pred)

small_core_predicted_mean_square_error = 0
for err in small_error_pred:
    small_core_predicted_mean_square_error += pow((err - small_uerror_pred), 2)
small_core_predicted_mean_square_error = math.sqrt(small_core_predicted_mean_square_error / len(small_error_pred))

#=================

#=================

small_error_next = []
for small_error_quantum in small_core_next_quantum_error:
    s_p = 0
    s_r = 0
    for small_error in small_error_quantum:
        if small_error[1].startswith("*") or small_error[1].startswith("?"):
            small_error[1] = small_error[1][1:]

        small_error = np.array(small_error)
        small_error = small_error.astype(np.float)

        if small_error[0] == 0:
            continue
        s_p += small_error[1]
        s_r += small_error[0]

    s_p = s_p / len(small_error_quantum)
    s_r = s_r / len(small_error_quantum)
    small_error_next.append(abs(s_p - s_r) / s_r)

small_uerror_next = sum(small_error_next) / len(small_error_next)

small_core_next_quantum_mean_square_error = 0
for err in small_error_next:
    small_core_next_quantum_mean_square_error += pow((err - small_uerror_next), 2)
small_core_next_quantum_mean_square_error = math.sqrt(small_core_next_quantum_mean_square_error / len(small_error_next))

#=================

small_error_ = []
for small_error_quantum in small_core_errors:
    small_error_quantum_percentage = []
    small_error_quantum_meansquare = []
    s_p = 0
    s_r = 0
    for small_error in small_error_quantum:
        if small_error[1].startswith("*") or small_error[1].startswith("?"):
            small_error[1] = small_error[1][1:]

        small_error = np.array(small_error)
        small_error = small_error.astype(np.float)

        if small_error[0] == 0:
            continue
        s_p += small_error[1]
        s_r += small_error[0]
        small_error_quantum_meansquare.append(pow((small_error[1] - small_error[0]), 2))
        small_error_quantum_percentage.append((small_error[1] - small_error[0]) / small_error[0])

    s_p = s_p / len(small_error_quantum)
    s_r = s_r / len(small_error_quantum)
    small_error_.append(abs(s_p - s_r) / s_r)
    small_percentage_error.append(sum(small_error_quantum_percentage) / len(small_error_quantum_percentage))

small_uerror = sum(small_error_) / len(small_error_)

small_std_error = 0
for err in small_error_:
    small_std_error += pow((err - small_uerror), 2)
small_std_error = math.sqrt(small_std_error / len(small_error_))

#=======

system_error_pred = []
for s_error in system_predicted_error:
    if s_error[0] == 0:
        continue

    system_error_pred.append(((abs(s_error[1] - s_error[0])) / s_error[0]))

system_uerror_pred = sum(system_error_pred) / len(system_error_pred)
system_predicted_mean_square_error = 0
for err in system_error_pred:
    system_predicted_mean_square_error += pow((err - system_uerror_pred), 2)
system_predicted_mean_square_error = math.sqrt((system_predicted_mean_square_error / len(system_error_pred)))

#=======

#=======

system_error_next = []
for s_error in system_next_quantum_error:
    if s_error[0] == 0:
        continue

    system_error_next.append(((abs(s_error[1] - s_error[0])) / s_error[0]))

system_uerror_next = sum(system_error_next) / len(system_error_next)
system_next_quantum_mean_square_error = 0
for err in system_error_next:
    system_next_quantum_mean_square_error += pow((err - system_uerror_next), 2)
system_next_quantum_mean_square_error = math.sqrt((system_next_quantum_mean_square_error / len(system_error_next)))

#=======

system_error_ = []
for s_error in system_error:
    if s_error[0] == 0:
        continue

    system_error_.append(((abs(s_error[1] - s_error[0])) / s_error[0]))
    system_mean_square_error += pow((s_error[1] - s_error[0]), 2)
    system_percentage_error.append((s_error[1] - s_error[0]) / s_error[0])
    diff_system.append(s_error[1] - s_error[0])

system_uerror = sum(system_error_) / len(system_error_)
system_std_error = 0
for err in system_error_:
    system_std_error += pow((err - system_uerror), 2)
system_std_error = math.sqrt((system_std_error / len(system_error_)))


big_mean_square_error = big_mean_square_error / len(big_core_errors)
small_mean_square_error = small_mean_square_error / len(small_core_errors)
system_mean_square_error = system_mean_square_error / len(system_error)

big_std = np.std(big_percentage_error)
small_std = np.std(small_percentage_error)
system_std = np.std(system_percentage_error)

big_percentage_error = sum(big_percentage_error) / len(big_core_errors)
small_percentage_error = sum(small_percentage_error) / len(small_core_errors)
system_percentage_error = sum(system_percentage_error) / len(system_error)

# diff_big = np.array(diff_big)
# diff_small = np.array(diff_small)
# diff_system = np.array(diff_system)

s_ipc = s_ipc / quantum_count

with open("IpcError.txt", "a") as myfile:
    myfile.write(fname + "\nbig_std_error_whole : " + str(big_std_err) + "\nbig_std_error_pred : " + str(big_core_predicted_mean_square_error) + "\nbig_std_error_next_quantum : " + str(big_core_next_quantum_mean_square_error) +"\nsmall_std_error_whole : " + str(small_std_error) + "\nsmall_std_error_pred : " + str(small_core_predicted_mean_square_error) + "\nsmall_std_error_next : " + str(small_core_next_quantum_mean_square_error) + "\nsystem_std_whole : " + str(system_std_error) + "\nsystem_std_pred: " + str(system_predicted_mean_square_error) + "\nsystem_std_next : " + str(system_next_quantum_mean_square_error) + "\n\n")
