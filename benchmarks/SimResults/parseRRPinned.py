import sys
import numpy as np

fname = sys.argv[1]
quantums = []

with open(fname) as f:
    content = f.readlines()
content = [x.strip() for x in content]

count = 100
is_quantum = False
quantum = []
for line in content:
    if line.startswith("----------- Qu"):
        quantum.append(line)
        is_quantum = True
    elif line.startswith("--------------------"):
        quantum.append(line)
        quantums.append(quantum)
        quantum = []
        is_quantum = False
    elif is_quantum:
        quantum.append(line)

quantum_ipc = []
quantum_ipc.append([0,0])

t_ipc = 0
for quantum in quantums:
    quantum_count = quantum[0].split()
    quantum_count = quantum_count[2]
    count += 1
    ipc = quantum[2].split()
    total_ipc = 0
    for per_ipc in ipc[1:]:
        total_ipc += float(per_ipc)
    t_ipc += total_ipc
    quantum_ipc.append([quantum_count, total_ipc])

print fname
print t_ipc / count
#
# threads = []
#
# for thread in quantums[0][4:7]:
#     threads.append(thread.split()[1:3])
#
# threads.append(quantums[0][4].split()[1:3])
#
# quantums = quantums[1:]
#
# big_core_errors = []
# small_core_errors = []
# system_error = []
#
# for quantum in quantums:
#     temp = []
#     for line in quantum:
#         if line[0].isdigit():
#             temp.append(line.split()[1:3])
#     small_errors = []
#     s_predicted = 0
#     s_real = 0
#     for prev_t, t in zip(threads, temp):
#         if not t[0].startswith("*") and not t[0].startswith("?"):
#             big_core_errors.append([t[0], prev_t[0]])
#             s_predicted += float(prev_t[0][1:] if prev_t[0].startswith("*") or prev_t[0].startswith("?") else prev_t[0])
#             s_real += float(t[0][1:] if t[0].startswith("*") or t[0].startswith("?") else t[0])
#         if not t[1].startswith("*") and not t[1].startswith("?"):
#             small_errors.append([t[1], prev_t[1]])
#             s_predicted += float(prev_t[1][1:] if prev_t[1].startswith("*") or prev_t[1].startswith("?") else prev_t[1])
#             s_real += float(t[1][1:] if t[1].startswith("*") or t[1].startswith("?") else t[1])
#     system_error.append([s_real, s_predicted])
#     threads = temp
#     small_core_errors.append(small_errors)
#
# print small_core_errors
#
# big_mean_square_error = 0
# small_mean_square_error = 0
#
# big_percentage_error = []
# small_percentage_error = []
#
# diff_small = []
# diff_big = []
#
# system_mean_square_error = 0
# system_percentage_error = []
# diff_system = []
#
#
# for big_error in big_core_errors:
#     if big_error[1].startswith("*") or big_error[1].startswith("?"):
#         big_error[1] = big_error[1][1:]
#
#     big_error = np.array(big_error)
#     big_error = big_error.astype(np.float)
#
#     if big_error[0] == 0:
#         continue
#
#     big_mean_square_error += pow((big_error[1] - big_error[0]), 2)
#
#     big_percentage_error.append((big_error[1] - big_error[0]) / big_error[0])
#     diff_big.append(big_error[1] - big_error[0])
#
#
# for small_error_quantum in small_core_errors:
#     small_error_quantum_percentage = []
#     small_error_quantum_meansquare = []
#     for small_error in small_error_quantum:
#         if small_error[1].startswith("*") or small_error[1].startswith("?"):
#             small_error[1] = small_error[1][1:]
#
#         small_error = np.array(small_error)
#         small_error = small_error.astype(np.float)
#
#         if small_error[0] == 0:
#             continue
#
#         small_error_quantum_meansquare.append(pow((small_error[1] - small_error[0]), 2))
#         small_error_quantum_percentage.append((small_error[1] - small_error[0]) / small_error[0])
#
#     small_mean_square_error += (sum(small_error_quantum_meansquare) / len(small_error_quantum_meansquare))
#     small_percentage_error.append(sum(small_error_quantum_percentage) / len(small_error_quantum_percentage))
#
# for s_error in system_error:
#     if s_error[0] == 0:
#         continue
#
#     system_mean_square_error += pow((s_error[1] - s_error[0]), 2)
#     system_percentage_error.append((s_error[1] - s_error[0]) / s_error[0])
#     diff_system.append(s_error[1] - s_error[0])
#
#
#
# big_mean_square_error = big_mean_square_error / len(big_core_errors)
# small_mean_square_error = small_mean_square_error / len(small_core_errors)
# system_mean_square_error = system_mean_square_error / len(system_error)
#
# big_std = np.std(big_percentage_error)
# small_std = np.std(small_percentage_error)
# system_std = np.std(system_percentage_error)
#
# big_percentage_error = sum(big_percentage_error) / len(big_core_errors)
# small_percentage_error = sum(small_percentage_error) / len(small_core_errors)
# system_percentage_error = sum(system_percentage_error) / len(system_error)
#
# # diff_big = np.array(diff_big)
# # diff_small = np.array(diff_small)
# # diff_system = np.array(diff_system)
#
#
#
# with open("IpcError.txt", "a") as myfile:
#     myfile.write(fname + "\nbig_mean_square_error : " + str(big_mean_square_error) + "\nsmall_mean_square_error : " + str(small_mean_square_error) + "\nsystem_mean_square_error : " + str(system_mean_square_error) +"\nbig_percentage_error : " + str(big_percentage_error) + "\nsmall_percentage_error : " + str(small_percentage_error) + "\nsystem_percentage_error : " + str(system_percentage_error) + "\nbig_std : " + str(big_std) + "\nsmall_std : " + str(small_std) + "\nsystem_std : " + str(system_std) + "\n ")
